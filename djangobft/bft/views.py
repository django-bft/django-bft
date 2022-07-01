from django.core.exceptions import ValidationError
from django.core.files.uploadhandler import StopUpload
from django.core.mail import send_mail, mail_admins
from wsgiref.util import FileWrapper
from django.urls import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.middleware.csrf import get_token
from .forms import EmailForm, SubmissionForm
from .models import File, Email, Submission
from string import Template
from . import app_settings
import json
import logging
import mimetypes
import os
import re
import math
import ast

# import ldap


def display_index(request):
    """
    View that displays main page.

    :Return: render
    """

    upload_limit = app_settings.MAX_UPLOAD_SIZE / 1024 / 1024 / 1024
    data = {
        "upload_limit": math.floor(upload_limit),
        "csrf_token_value": get_token(request),
        "upload_size_limit": app_settings.MAX_UPLOAD_SIZE,
        "app_name": app_settings.APP_NAME,
    }

    return render(request, "index.html", data)


def display_about(request):
    """
    View that displays about page.

    :Return: render
    """

    data = {
        "app_name": app_settings.APP_NAME,
    }

    return render(request, "about.html", data)


def get_file(request, file_slug=None, file_name=None):
    """
    Sends a file to the browser for download.

    :Return: HttpResponse
    """

    if file_slug:
        file_obj = get_object_or_404(File, slug=file_slug)

        if not file_name:
            return HttpResponseRedirect(
                reverse(
                    "file", kwargs={"file_slug": file_slug, "file_name": os.path.basename(file_obj.file_upload.name)}
                )
            )

        elif file_name != os.path.basename(file_obj.file_upload.name):
            raise Http404

        submission = Submission.objects.get(pk=file_obj.submission.pk)

        mimetype, encoding = mimetypes.guess_type(file_name)
        mimetype = mimetype or "application/force-download"

        response = HttpResponse(FileWrapper(file_obj.file_upload), content_type=mimetype)

        response["Content-Length"] = file_obj.file_upload.size
        response["Content-Disposition"] = "attachment"
        if encoding:
            response["Content-Encoding"] = encoding

        if submission.anumbers:
            bft_auth = request.session.get("bft_auth")
            if bft_auth and bft_auth in submission.anumbers.lower():
                return response
            else:
                return HttpResponseRedirect(reverse("files", args=[submission.slug]))
        else:
            return response
    else:
        raise Http404


def list_files(request, submission_slug=None):
    """
    Outputs all the files for a submission.

    :Return: render
    """

    data = {}
    file_list = []

    # process login if needed
    login_user(request)

    if ("slug") in request.GET and request.GET["slug"].isalnum():
        submission_slug = request.GET["slug"]
    elif submission_slug is None:
        raise Http404

    data["submission_slug"] = submission_slug
    submission = get_object_or_404(Submission, slug=submission_slug)
    files = File.objects.filter(submission=submission)

    if files:
        for file in files:
            h = "https" if request.is_secure() else "http"
            url = f"{h}://{request.META['SERVER_NAME']}{file.get_short_url()}"
            file_list.append(url)
    else:
        raise Http404

    # send out emails
    if file_list and not submission.email_sent:
        if submission.type == "email":
            process_sender(submission, file_list, has_email=True)
            process_recipients(submission, file_list)
        else:
            process_sender(submission, file_list)

        # emails have been send, flag to not send again.
        submission.email_sent = True
        submission.save()

    # Remove empty strings from submission.anumbers if no a-numbers are specified or there are empty fields
    if submission.anumbers and "" in submission.anumbers:
        # Convert string that looks like a list to a string
        submission.anumbers = ast.literal_eval(submission.anumbers)
        submission.anumbers = list(filter(("").__ne__, submission.anumbers))

    if submission.anumbers:
        bft_auth = request.session.get("bft_auth")
        if bft_auth and bft_auth in submission.anumbers.lower():
            data["files"] = file_list
            return render(request, "files.html", data)
        elif request.POST and ("anumber") in request.POST:
            data["invalid_credentials"] = True

        # return to login if not authenticated or invalid credentials
        return render(request, "login.html", data)

    else:
        data["files"] = file_list
        return render(request, "files.html", data)


def render_vars(request):
    """
    Renders settings into a javascript file that can be read by the browser.

    :Return: render
    """

    data = {
        "upload_size_limit": app_settings.MAX_UPLOAD_SIZE,
    }

    return render(request, "inc/bftvars.js", data, content_type="text/javascript")


@transaction.atomic
def process_submission(request):
    """
    Processes the submission and returns back to the browser.

    :Return: HttpResponse
    """
    data = {
        "error": False,
    }

    submission = None

    try:
        # force the request to be ajax.
        request.META["HTTP_X_REQUESTED_WITH"] = "XMLHttpRequest"

        if request.method == "POST" and "type" in request.POST:

            # if submission is of type email, process the email form
            if "email" in request.POST["type"]:
                form = EmailForm(request.POST)

            # else if submission is of type link, process the submission form
            elif "link" in request.POST["type"]:
                form = SubmissionForm(request.POST)

            else:
                logging.error("Post Type Error: %s", "Incorrect Post type", extra={"request": request})
                raise ValidationError("Incorrect Post type.")

            form.instance.submit_ip = request.META["REMOTE_ADDR"]
            form.instance.browser_meta = f"{request.META['HTTP_USER_AGENT']}  {request.POST['flash_meta']}"

            if form.is_valid():
                form.save()
            else:
                raise ValidationError(form.errors)

            submission = form.instance
            data["submission_slug"] = submission.slug

        # if no request.POST, throw error
        else:
            logging.error("Post Type Error: %s", "No Post or Post type", extra={"request": request})
            raise ValidationError("No Post or Post type.")

    except StopUpload:
        data["error"] = True
        data["messages"] = ["The file you uploaded exceeds the allowed limit!"]

    except IOError:
        data["error"] = True
        data["messages"] = [
            "Your file upload has timed out."
            "  This might be due to problems with your flash player."
            "Please try your upload using the"
            f'<a href="{reverse("noflash")}">No Flash</a> version.'
        ]

    except ValidationError as e:
        # delete the sumbission if there are errors.
        # if submission:
        # 	submission.delete()
        data["error"] = True
        data["messages"] = e.messages

    except Exception:
        raise

    out = json.dumps(data)

    return HttpResponse(out)


def process_sender(submission, files, has_email=False):
    """
    Helper function that processes sender and emails them with a link(s) to their files

    :Return: Void
    """

    if has_email:
        email = Email.objects.get(pk=submission)
        str_email = "Your file(s) have also been sent to the " "following recipient(s) as you requested."
        str_recipients = "\n".join(email.recipients.split(","))
        str_message = (
            """



---Email Message to recipients---

%s

"""
            % email.message
        )

    else:
        str_email = ""
        str_recipients = ""
        str_message = ""

    template = """
Greetings:

Thanks for using $appname.

Your file(s) are waiting for you at:
$files

$email
$recipients
$message

The file(s) will be available for $days days after which they will be removed. 
To learn more visit: http://bft.usu.edu/about
"""

    template = Template(template)
    email_body = template.substitute(
        files="\n".join(files),
        email=str_email,
        recipients=str_recipients,
        message=str_message,
        days=app_settings.UPLOAD_EXPIRATION_DAYS,
        appname=app_settings.APP_NAME,
    )

    send_mail(
        f"[{app_settings.APP_NAME}] A file has been sent to you",
        email_body,
        app_settings.REPLY_EMAIL,
        [submission.email_address],
    )

    return


def process_recipients(submission, files):
    """
    Helper function that processes recipients and emails them a link to the file(s)

    :Return: Void
    """

    email = Email.objects.get(pk=submission)

    template = """
$message

$files

---------------------

These files were sent to you by $appname service.
The file(s) will be available for $days days after which they will be removed.
To learn more visit: http://bft.usu.edu/about

This system is still in beta, and as such, please send any comments or bugs to $reply
"""
    template = Template(template)
    email_body = template.substitute(
        sender=f"{email.first_name} {email.last_name}",
        sender_email=email.email_address,
        files="\n".join(files),
        message=email.message,
        reply=app_settings.REPLY_EMAIL,
        appname=app_settings.APP_NAME,
        days=app_settings.UPLOAD_EXPIRATION_DAYS,
    )

    send_mail(
        f"[{app_settings.APP_NAME}] A file has been sent to you",
        re.sub(r"^https?:\/\/.*[\r\n]*", "[link not allowed]", email_body, flags=re.MULTILINE),
        email.email_address,
        ast.literal_eval(email.recipients),
    )

    return


def upload(request):
    """
    Helper function that processes the file upload form uploadifive.

    :Return: HttpResponse of 0 or 1
    """
    try:
        if request.method == "POST" and "file_upload" in request.FILES and "slug" in request.GET:
            upload = File()
            upload.file_upload = request.FILES["file_upload"]
            upload.submission = Submission.objects.get(slug=request.GET["slug"])
            upload.save()
            return HttpResponse(1)

        else:
            logging.error("Upload Error", extra={"request": request})
            return HttpResponse(0)

    except StopUpload:
        raise

    except:
        logging.error("Upload Error", extra={"request": request})
        return HttpResponse(0)


def login_user(request):
    """
    **USU Specific**

    Processes login for USU credential by setting a session token 'bft_auth'
    in the session scope.

    :Return: Void
    """

    # if request.POST and ("anumber") in request.POST and ("password") in request.POST:
    #     auth = AuthWebservice()

    #     user = auth.authenticate(username=request.POST["anumber"].lower(), password=request.POST["password"])

    #     if user:
    #         request.session["bft_auth"] = user["username"].lower()

    # return

    # NEW LDAP STUFF WILL GO HERE


def send_feedback(request):
    """
    Processes submission from feedback forms and emails Django admins.

    :Return: HttpResponse of 0 or 1
    """

    if request.POST and request.POST.get("message", "") and request.POST.get("email", ""):

        mail_admins(
            subject="[PAD User Feedback] BFT",
            message=f"Feedback from the BFT Support form:\n\n{request.POST['email']}\n\n{request.POST['message']}",
        )
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def error_413(request):

    data = {"error": True, "messages": ["The file you uploaded exceeds the allowed limit!"]}

    out = f"{'<textarea>'}{json.dumps(data)}{'</textarea>'}"

    return HttpResponse(out)


def server_error(request, template_name="500.html"):

    logging.error("Upload Error", extra={"request": request})

    t = loader.get_template(template_name)
    print(request)
    return HttpResponseServerError(t.render)
