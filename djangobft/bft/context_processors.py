from bft.app_settings import CONFIG as app_settings
from django.conf import settings
from django.core.urlresolvers import reverse


def bft(request):
    abs_static_url = f"http{'s' if request.is_secure() else ''}://{request.META['SERVER_NAME']}{settings.STATIC_URL}"

    return {
        "app_name": app_settings.APP_NAME,
        "use_flash": app_settings.USE_FLASH,
        "expiry_days": app_settings.UPLOAD_EXPIRATION_DAYS,
        "reply_email": app_settings.REPLY_EMAIL,
        "show_feedback": app_settings.SHOW_FEEDBACK,
        "feedback_url": reverse("feedback"),
        "abs_static_url": abs_static_url,
    }
