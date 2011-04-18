from bft import app_settings
from django.conf import settings
from django.core.urlresolvers import reverse

def bft(request):
	
	abs_static_url = "http%s://%s%s" % (
			's' if request.is_secure() else None,
			request.META['SERVER_NAME'], 
			settings.STATIC_URL[1:]
	)
		
	# Show the password field if RANDOM_PASS is False:
	show_password_input = False if app_settings.RANDOM_PASS else True
		
	return { 
				'app_name' : app_settings.APP_NAME,
				'use_flash' : app_settings.USE_FLASH,
				'expiry_days' : app_settings.UPLOAD_EXPIRATION_DAYS,
				'reply_email' : app_settings.REPLY_EMAIL,
				'show_feedback' : app_settings.SHOW_FEEDBACK,
				'feedback_url' : reverse('feedback'),
				'show_password_input' : show_password_input,
				'abs_static_url' : abs_static_url
			}
