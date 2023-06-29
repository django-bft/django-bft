from .app_settings import CONFIG as app_settings


def bft(request):
    return {
        "app_name": app_settings.APP_NAME,
        "expiry_days": app_settings.UPLOAD_EXPIRATION_DAYS,
        "reply_email": app_settings.REPLY_EMAIL,
    }
