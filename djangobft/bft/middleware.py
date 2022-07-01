from app_settings import CAPTCHA_VERIFY_URL, CAPTCHA_KEY, USE_CAPTCHA, CAPTCHA_SUBNET_EXCLUDE
from django.utils import simplejson
import urllib


class VerifymeMiddleware(object):
    def process_request(self, request):

        url = request.get_full_path().split("/")[1]

        # Do not fire this middleware for the ajax progress pulling
        if USE_CAPTCHA and url not in ["progress"]:
            user_subnet = ".".join(request.META["REMOTE_ADDR"].split(".")[:2])

            if user_subnet not in CAPTCHA_SUBNET_EXCLUDE:

                try:
                    url = CAPTCHA_VERIFY_URL + "key/" + CAPTCHA_KEY
                    response = simplejson.load(urllib.urlopen(url))

                    if not response["success"]:
                        Exception(
                            "Verifyme Error: The URLs for Verifyme is invalid.  " "Please check your app_settings.py"
                        )

                except IOError:
                    raise Exception(
                        "Verifyme Error:  There is an error communicating "
                        "with the Verifyme Server. Please check your settings."
                    )

        return None
