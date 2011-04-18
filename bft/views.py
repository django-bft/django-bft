from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadhandler import StopUpload
from django.core.mail import send_mail, mail_admins
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseServerError, \
    HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.utils import simplejson
from forms import EmailForm, SubmissionForm
from hashlib import md5
from models import File, Email, Submission
from string import Template
from utils.json_utils import JsonResponse
import app_settings
import mimetypes
import os

# Try to import recaptcha
if app_settings.USE_RECAPTCHA:
    try: 
        from recaptcha.client import captcha
    except ImportError:
        raise Exception('Could not import recaptcha. Please make sure the ' 
                    'recaptcha is installed on your python path.'
                    ' http://pypi.python.org/pypi/recaptcha-client')
 
# Set replay email constant      
REPLY_EMAIL = getattr(app_settings, 'REPLY_EMAIL', settings.SERVER_EMAIL)

def display_index(request, use_flash=app_settings.USE_FLASH):
    """
    View that displays main page.
        
    :Return: render_to_response
    """

    upload_limit = app_settings.MAX_UPLOAD_SIZE / 1024 / 1024 / 1024
    data = {
        'use_flash' : use_flash,
        'use_captcha' : use_captcha(request),
        'upload_limit' : upload_limit
    }
    
    return render_to_response('bft/index.html', data, RequestContext(request))


def display_about(request, use_flash=app_settings.USE_FLASH):
    """
    View that displays about page.
        
    :Return: render_to_response
    """
    
    data = {
        'use_flash' : use_flash,
    }
    
    return render_to_response('bft/about.html', data, RequestContext(request))


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
                    'file', 
                    kwargs={
                        'file_slug' : file_slug, 
                        'file_name': os.path.basename(file_obj.file_upload.name)
                    }
                )
            )
        elif file_name != os.path.basename(file_obj.file_upload.name):
            raise Http404 
            
        submission = Submission.objects.get(pk=file_obj.submission.pk)
        
        mimetype, encoding = mimetypes.guess_type(file_name) 
        mimetype = mimetype or 'application/force-download' 
    
        response = HttpResponse(
                        FileWrapper(file_obj.file_upload), 
                        mimetype=mimetype
                    ) 
        
        response['Content-Length'] = file_obj.file_upload.size 
        response["Content-Disposition"] = "attachment" 
        if encoding: 
            response["Content-Encoding"] = encoding 

        if submission.password:
            session_slug = request.session.get('bft_auth', '')
            
            if session_slug in submission.slug:
                return response
            else:
                return HttpResponseRedirect(reverse('files', args=[submission.slug]))
        else:
            return response
    else:
        raise Http404 

def list_files(request, submission_slug=None, use_flash=app_settings.USE_FLASH):
    """
    Outputs all the files for a submission.
        
    :Return: render_to_response
    """

    data = {
        'use_flash' : app_settings.USE_FLASH
    }
    file_list = []

    #process login if needed
    login(request, submission_slug)

    if request.GET.has_key('slug') and request.GET['slug'].isalnum():
        submission_slug = request.GET['slug']
    elif submission_slug is None:
        raise Http404
    
    data['submission_slug'] = submission_slug
    submission = get_object_or_404(Submission, slug=submission_slug)
    files = File.objects.filter(submission=submission)
    
    if files:
        for file in files:
            if request.is_secure():
                h = 'https'
            else:
                h = 'http'
            url = '%s://%s%s' % (h, request.META['SERVER_NAME'], file.get_short_url())
            file_list.append(url)
    else:
        raise Http404 
    
    #send out emails    
    if file_list and not submission.email_sent:
        if submission.type == 'email':
            process_sender(submission, file_list, has_email=True)
            process_recipients(submission, file_list)
        else:
            process_sender(submission, file_list)
        
        #emails have been send, flag to not send again.
        submission.email_sent = True
        submission.save()
    
    if submission.password:
    	session_slug = request.session.get('bft_auth', '')
        
        if session_slug in submission.slug:
            data['files'] = file_list
            return render_to_response("bft/files.html", data, RequestContext(request))
        elif request.POST and request.POST.has_key('password'):
            data['invalid_credentials'] = True
        
        #return to login if not authenticated or invalid credentials
        return render_to_response("bft/login.html", data, RequestContext(request))
    
    else:
        data['files'] = file_list
        return render_to_response("bft/files.html", data, RequestContext(request))


def render_vars(request, use_flash=app_settings.USE_FLASH):
    """
    Renders settings into a javascript file that can be read by the browser.
        
    :Return: render_to_response
    """
    
    data = {
        'recaptcha_pub_key' : app_settings.RECAPTCHA_PUB_KEY,
        'upload_size_limit' : app_settings.MAX_UPLOAD_SIZE,
        'use_flash' : use_flash,
        'use_captcha' : use_captcha(request),
    }
    
    if 'noflash' in request.GET:
        data['use_flash'] = False
    
    return render_to_response(
                'bft/inc/bftvars.js', 
                data, 
                RequestContext(request), 
                mimetype="text/javascript"
            )


@transaction.commit_on_success()
def process_submission(request):
    """
    Processes the submission and returns back to the browser.
        
    :Return: HttpResponse
    """
    
    data = {
        'error' : False,
    }
    
    submission = None
    email_form = None

    try:
        #force the request to be ajax.
        request.META['HTTP_X_REQUESTED_WITH'] = "XMLHttpRequest"
        
        if request.method == 'POST' and request.POST.has_key('type'):
            
            #if submission is of type email, process the email form
            if 'email' in request.POST['type']:
                form, email_form = SubmissionForm(request.POST), EmailForm(request.POST)

            #else if submission is of type link, process the submission form
            elif 'link' in request.POST['type']:
                form = SubmissionForm(request.POST)
                
            else:
                raise ValidationError('Incorrect Post type.')
                
            form.instance.submit_ip = request.META['REMOTE_ADDR'] 
            form.instance.browser_meta = "%s  %s" % (
				request.META['HTTP_USER_AGENT'], 
				request.POST['flash_meta']
			)

            if form.is_valid():
                #save form
                form.save()
                #save email form
                if email_form: 
                    #set the pk from the submission
                    email_form.instance.submission = form.instance
                    if email_form.is_valid():
                        email_form.save()
                    else:    
                        raise ValidationError(email_form.errors)
            else:
                raise ValidationError(form.errors)
                
            submission = form.instance
            data['submission_slug'] = submission.slug
            data['submission_url'] = reverse('files', args=[submission.slug])
            
            #process files if uploaded via html
            upload_html(request, form.instance)
            
        #if no request.POST, throw error        
        else:
            raise ValidationError('No Post or Post type.')
        
    except StopUpload:
        data['error'] = True
        data['messages'] = ['The file you uploaded exceeds the allowed limit!']

    except IOError:
        data['error'] = True
        data['messages'] = [
            'Your file upload has timed out.'
            '  This might be due to problems with your flash player.'
            'Please try your upload using the' 
            '<a href="%s">No Flash</a> version.' % reverse('noflash')
        ]

    except ValidationError, e:
        data['error'] = True
        data['messages'] = e.messages
        
    except Exception:
        raise
    
    out = "<textarea>%s</textarea>" % simplejson.dumps(data)
    
    return HttpResponse(out)


def process_sender(submission, files, has_email=False):
    """
    Helper function that processes sender and emails them with a link(s) to their files
    
    :Return: Void
    """
    
    if app_settings.ENCRYPT_PASS and submission.password:
        str_password = (
			'Note: This submission is password protected.  '
			'Please make sure you let your recipients know the password.'
		)
    elif submission.password:
        str_password = 'The password for this submission is:  %s' % submission.password
    else:
        str_password = ''
        
    if has_email:
        email = Email.objects.get(submission=submission)
        str_email = (
			'Your file(s) have also been sent to the '
			'following recipient(s) as you requested.'
		)
        str_recipients = '\n'.join(email.recipients.split(','))
        str_message = '''



---Email Message to recipients---

%s

''' % email.message

    else:
        str_email = ''
        str_recipients = ''
        str_message = ''
    
    template = '''
Greetings:
    
Thanks for using $appname.

Your file(s) are waiting for you at:
$files    

$email
$recipients

$password
$message

The file(s) will be available for $days days after which they will be removed. 
'''    

    template = Template(template)
    email_body = template.substitute(
        files='\n'.join(files),
        email=str_email,
        recipients=str_recipients,
        password=str_password,
        message=str_message,
        days=app_settings.UPLOAD_EXPIRATION_DAYS,
        appname=app_settings.APP_NAME    
    )
    
    send_mail(
        '[%s] A file has been sent to you' % app_settings.APP_NAME, 
        email_body, REPLY_EMAIL, 
        [submission.email_address]
    )
        
    return

def process_recipients(submission, files):
    if app_settings.ENCRYPT_PASS and submission.password:
        password = (
			'Note: This submission is password protected.  Please contact %s '
			'if you do not know the password already.' % submission.email_address
		)
    elif submission.password:
        password = 'The password for this submission is:  %s' % submission.password

    email = Email.objects.get(submission=submission)
    
    template = '''
$message    

$password

$files

---------------------

These files were sent to you by $appname service.
The file(s) will be available for $days days after which they will be removed. 

This system is still in beta, and as such, please send any comments or bugs to $reply
'''
    template = Template(template)
    email_body = template.substitute(
        sender='%s %s' % (email.first_name, email.last_name),
        sender_email=submission.email_address,
        files='\n'.join(files),
        password=password,
        message=email.message,
        reply=REPLY_EMAIL,
        appname=app_settings.APP_NAME,
        days=app_settings.UPLOAD_EXPIRATION_DAYS
    )
    
    send_mail(
        '[%s] A file has been sent to you' % app_settings.APP_NAME, 
        email_body, 
        email.email_address, 
        email.recipients.split(',')
    )

    return

def upload_html(request, submission):
    """
    Helper function that processes the file upload.  Used by the 'no flash' version.
    
    :Return: Void
    """
    
    if request.FILES:
        for file in request.FILES:
            upload = File()
            upload.submission = submission
            upload.file_upload = request.FILES[file]
            upload.save()
            
    return


def upload_flash(request):
    """
    Helper function that processes the file upload.  Used by flash player.
    
    :Return: HttpResponse of 0 or 1
    """
    
    try:
        if (request.method == 'POST' and 'file_upload' 
            in request.FILES and 'slug' in request.GET):
            upload = File()
            upload.file_upload = request.FILES['file_upload']
            upload.submission = Submission.objects.get(slug=request.GET['slug'])
            upload.save()
            return HttpResponse(1)
        
        else:
            return HttpResponse(0)
    
    except StopUpload:
        raise

    except:
        return HttpResponse(0)


def submit_captcha(request):
    """
    Function that calls reCaptcha's webservice to determine if
    correct or not.
    
    :Return: HttpResponse of 0 or 1
    """
    
    if (request.POST and request.POST.has_key('recaptcha_challenge_field') 
        and request.POST.has_key('recaptcha_response_field')):
        check_captcha = captcha.submit(
            request.POST['recaptcha_challenge_field'],
            request.POST['recaptcha_response_field'],
            app_settings.RECAPTCHA_PRIVATE_KEY,
            request.META['REMOTE_ADDR']
        )
        
        if check_captcha.is_valid:
            return HttpResponse(1)
        else:
            return HttpResponse(0)
    else:
        return HttpResponse(0)

        
def use_captcha(request):
    """
    Function to check whether or not to use reCaptcha.
    
    :Return: True or False
    """
    
    if app_settings.USE_RECAPTCHA:
        if app_settings.RECAPTCHA_SUBNET in request.META['REMOTE_ADDR']:
            return False
        else:
            return True


def html_progress(request):
    """
    Function that is used by the 'no flash' version.
    jQuery uses this via ajax to poll the progress at a set interval.
    
    :Return: JsonResponse with information about the progress of an upload.
    """
    
    progress_id = None

    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']

    if progress_id:
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        if not data:
            data = { 'state' : 'error' }
        elif data['state'] == 'done':
            data = { 'state' : 'done' }
            cache.delete(cache_key)
    else:
        data = {'state' : 'error'}
        
    return JsonResponse(data)


def login(request, submission_slug=None):
    """
    
    Processes login for password protected files by setting a token 'bft_auth'
    in the session scope.
    
    :Return: Void
    """
    
    if request.POST and request.POST.has_key('password'):
        
        if app_settings.ENCRYPT_PASS and not app_settings.RANDOM_PASS:
            password = md5(request.POST['password']).hexdigest()
        else:
            password = request.POST['password']
        
        valid_password = Submission.objects.filter(
			slug=submission_slug, 
			password=password
		)
        
        if valid_password:
            request.session['bft_auth'] = submission_slug
            
    return


def send_feedback(request):
    """
    Processes submission from feedback forms and emails Django admins.
    
    :Return: HttpResponse of 0 or 1
    """
    
    if request.POST and request.POST.get('message', '') and request.POST.get('email', ''):
        mail_admins(
            subject='[%s] User Feedback' % app_settings.APP_NAME,
            message="Feedback from:\n\n%s\n\n%s" % (
				request.POST['email'], 
				request.POST['message']
			)
        )
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def error_413(request):
    
    data = {
        'error' : True,
        'messages' : ['The file you uploaded exceeds the allowed limit!']
    }
    
    out = "<textarea>%s</textarea>" % simplejson.dumps(data) 
    
    return HttpResponse(out)


def server_error(request, template_name='500.html'):
    
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))
