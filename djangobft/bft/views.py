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
from djangopad.webservices.auth import AuthWebservice
from forms import EmailForm, SubmissionForm
from models import File, Email, Submission
from string import Template
from utils.json_utils import JsonResponse
import app_settings
import logging
import mimetypes
import os
import re
import urllib


def display_index(request, use_flash=app_settings.USE_FLASH):
	"""
	View that displays main page.
		
	:Return: render_to_response
	"""

	upload_limit = app_settings.MAX_UPLOAD_SIZE / 1024 / 1024 / 1024
	data = {
		'use_flash' : use_flash,
		'use_captcha' : use_captcha(request),
		'upload_limit' : upload_limit,
		'captcha_key' : app_settings.CAPTCHA_KEY,
	}
	
	return render_to_response('index.html', data, RequestContext(request))


def display_about(request, use_flash=app_settings.USE_FLASH):
	"""
	View that displays about page.
		
	:Return: render_to_response
	"""
	
	data = {
		'use_flash' : use_flash,
	}
	
	return render_to_response('about.html', data, RequestContext(request))


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

		if submission.anumbers:
			bft_auth = request.session.get('bft_auth')
			if bft_auth and bft_auth in submission.anumbers.lower():
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
	login(request)

	if request.GET.has_key('slug') and request.GET['slug'].isalnum():
		submission_slug = request.GET['slug']
	elif submission_slug is None:
		raise Http404
	
	data['submission_slug'] = submission_slug
	submission = get_object_or_404(Submission, slug=submission_slug)
	files = File.objects.filter(submission=submission)
	
	if files:
		for file in files:
			h = 'https' if request.is_secure() else 'http'
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
	
	if submission.anumbers:
		bft_auth = request.session.get('bft_auth')
		if bft_auth and bft_auth in submission.anumbers.lower():
			data['files'] = file_list
			return render_to_response("files.html", data, RequestContext(request))
		elif request.POST and request.POST.has_key('anumber'):
			data['invalid_credentials'] = True
		
		#return to login if not authenticated or invalid credentials
		return render_to_response("login.html", data, RequestContext(request))
	
	else:
		data['files'] = file_list
		return render_to_response("files.html", data, RequestContext(request))


def render_vars(request, use_flash=app_settings.USE_FLASH):
	"""
	Renders settings into a javascript file that can be read by the browser.
		
	:Return: render_to_response
	"""
	
	data = {
		'captcha_key' : app_settings.CAPTCHA_KEY,
		'upload_size_limit' : app_settings.MAX_UPLOAD_SIZE,
		'use_flash' : use_flash,
		'use_captcha' : use_captcha(request),
	}
	
	if 'noflash' in request.GET:
		data['use_flash'] = False
	
	return render_to_response(
				'inc/bftvars.js',
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
	
	try:
		#force the request to be ajax.
		request.META['HTTP_X_REQUESTED_WITH'] = "XMLHttpRequest"
		
		if request.method == 'POST' and request.POST.has_key('type'):
			
			#if submission is of type email, process the email form
			if 'email' in request.POST['type']:
				form = EmailForm(request.POST)
				
			#else if submission is of type link, process the submission form
			elif 'link' in request.POST['type']:
				form = SubmissionForm(request.POST)
				
			else:
				logging.error(
					'Post Type Error: %s', 
					'Incorrect Post type',
					extra={'request':request})
				raise ValidationError('Incorrect Post type.')
				
			form.instance.submit_ip = request.META['REMOTE_ADDR'] 
			form.instance.browser_meta = "%s  %s" % \
				(request.META['HTTP_USER_AGENT'], request.POST['flash_meta'])

			if form.is_valid():
				form.save()
			else:
				raise ValidationError(form.errors)
				
			submission = form.instance
			data['submission_slug'] = submission.slug
			
			#process files if uploaded via html
			upload_html(request, form.instance)
			
		#if no request.POST, throw error		
		else:
			logging.error(
				'Post Type Error: %s', 
				'No Post or Post type',
				extra={'request':request})
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
		#delete the sumbission if there are errors.
		#if submission:
		#	submission.delete()
		data['error'] = True
		data['messages'] = e.messages
		
	except Exception:
		raise
	
	out = "%s%s%s" % ("<textarea>", simplejson.dumps(data), "</textarea>") 
	
	return HttpResponse(out)


def process_sender(submission, files, has_email=False):
	"""
	Helper function that processes sender and emails them with a link(s) to their files
	
	:Return: Void
	"""
	
	if has_email:
		email = Email.objects.get(pk=submission)
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
$message

The file(s) will be available for $days days after which they will be removed. 
To learn more visit: http://bft.usu.edu/about
'''	

	template = Template(template)
	email_body = template.substitute(
		files='\n'.join(files),
		email=str_email,
		recipients=str_recipients,
		message=str_message,
		days=app_settings.UPLOAD_EXPIRATION_DAYS,
		appname=app_settings.APP_NAME	
	)
	
	send_mail(
		'[%s] A file has been sent to you' % app_settings.APP_NAME,
		email_body, app_settings.REPLY_EMAIL,
		[submission.email_address]
	)
		
	return

def process_recipients(submission, files):
	"""
	Helper function that processes recipients and emails them a link to the file(s)
	
	:Return: Void
	"""
	
	email = Email.objects.get(pk=submission)
	
	template = '''
$message	

$files

---------------------

These files were sent to you by $appname service.
The file(s) will be available for $days days after which they will be removed. 
To learn more visit: http://bft.usu.edu/about

This system is still in beta, and as such, please send any comments or bugs to $reply
'''
	template = Template(template)
	email_body = template.substitute(
		sender='%s %s' % (email.first_name, email.last_name),
		sender_email=email.email_address,
		files='\n'.join(files),
		message=email.message,
		reply=app_settings.REPLY_EMAIL,
		appname=app_settings.APP_NAME,
		days=app_settings.UPLOAD_EXPIRATION_DAYS
	)
	
	send_mail(
		'[%s] A file has been sent to you' % app_settings.APP_NAME,
		re.sub(r'^https?:\/\/.*[\r\n]*', '[link not allowed]', email_body, flags=re.MULTILINE),
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
			logging.error('Flash Upload Error', extra={'request':request})
			return HttpResponse(0)
	
	except StopUpload:
		raise

	except:
		logging.error('Flash Upload Error', extra={'request':request})
		return HttpResponse(0)


def display_captcha(request):
	
	verifyme_params = {
	    'key' : app_settings.CAPTCHA_KEY,
	}

	url = app_settings.CAPTCHA_CHALLENGE_URL + '?' + urllib.urlencode(verifyme_params)
	data = simplejson.load(urllib.urlopen(url))

	return JsonResponse(data)


def submit_captcha(request):
	"""
	Function that calls Verifyme's webservice to determine if
	correct or not.
	
	:Return: HttpResponse of 0 or 1
	"""
	data = {}
	
	params = {
        'key' : app_settings.CAPTCHA_KEY,
        'questionid' : request.POST.get('verifyme_questionid'),
        'answer' : request.POST.get('verifyme_answer')
	}
	
	url = app_settings.CAPTCHA_VERIFY_URL + '?' + urllib.urlencode(params)
	response = simplejson.load(urllib.urlopen(url))
	
		
	if response['success']:
		data['success'] = True
	
	else:
		
		data['success'] = False
		if response.has_key('error_code') and response['error_code'] != 200:
			data['message'] = response['messages'][0]
		else:
			data['message'] = 'Invalid Response'
			
		logging.error(
			'Captcha Error: %s', 
			data['message'],
			extra={'request':request})
	
	return JsonResponse(data)

		
def use_captcha(request):
	"""
	Function to check whether or not to use reCaptcha.
	
	:Return: True or False
	"""
	
	if app_settings.USE_CAPTCHA:
		user_subnet = '.'.join(request.META['REMOTE_ADDR'].split('.')[:2])
		
		if user_subnet in app_settings.CAPTCHA_SUBNET_EXCLUDE:
			return False
		else:
			return True
			
	else:
		return False
		

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


def login(request):
	"""
	**USU Specific**
	
	Processes login for USU credential by setting a session token 'bft_auth'
	in the session scope.
	
	:Return: Void
	"""
	
	if request.POST and request.POST.has_key('anumber') and request.POST.has_key('password'):
		auth = AuthWebservice()
		
		user = auth.authenticate(
			username=request.POST['anumber'].lower(),
			password=request.POST['password']
		)
		
		if user:
			request.session['bft_auth'] = user['username'].lower()
			
	return


def send_feedback(request):
	"""
	Processes submission from feedback forms and emails Django admins.
	
	:Return: HttpResponse of 0 or 1
	"""
	
	if request.POST and request.POST.get('message', '') and request.POST.get('email', ''):
		
		mail_admins(
			subject='[PAD User Feedback] BFT',
			message="Feedback from the BFT Support form:\n\n%s\n\n%s" % (
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
	
	out = "%s%s%s" % ("<textarea>", simplejson.dumps(data), "</textarea>") 
	
	return HttpResponse(out)


def server_error(request, template_name='500.html'):
	
	logging.error('Flash Upload Error', extra={'request':request})
	
	t = loader.get_template(template_name)
	return HttpResponseServerError(t.render(RequestContext(request)))


