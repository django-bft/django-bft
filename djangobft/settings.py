import ast
import os
from pathlib import Path
from decouple import config


try:
    from .local_settings import *  # noqa: F403,F401
except ImportError:
    pass

SERVER_NAME = config("SERVER_NAME", default="localhost")

ADMINS = ast.literal_eval(config("ADMINS", default="[]"))

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="['*']").split(",")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-hw88ovvd%uxai(1tavbr_!+%kmym=e_yfvo-lp_@2fivop1cxq")

EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")

EMAIL_HOST = config("EMAIL_HOST", default="localhost")

DEBUG = config("DEBUG", default=False, cast=bool)

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default=[]).split(",")

SSL_PROXY = config("SSL_PROXY", default=False, cast=bool)
if SSL_PROXY:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_SAVE_EVERY_REQUEST = True

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "djangobft.bft",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "djangobft.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "djangobft.bft.context_processors.bft",
            ],
        },
    },
]

WSGI_APPLICATION = "djangobft.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB"),
        "USER": config("POSTGRES_USER"),
        "PASSWORD": config("POSTGRES_PASSWORD"),
        "HOST": "db",
        "PORT": "5432",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "bft_cache",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "MST"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SAML2_AUTH = {
    # Metadata configuration
    "METADATA_AUTO_CONF_URL": config("SAML2_AUTH_METADATA_URL", default=""),
    "DEFAULT_NEXT_URL": "/",
    # SAML authentication configuration
    "ENTITY_ID": config("SAML2_AUTH_ENTITY_ID", default=""),
    "ASSERTION_URL": config("SAML2_ASSERTION_URL", default=""),
    "NAMEID_FORMAT": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
    "CREATE_USER": True,
    "BINDING": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
    # Attribute mapping configuration
    "ATTRIBUTES_MAP": {
        "username": "name",
        "email": "emailAddress",
        "first_name": "givenName",
        "last_name": "surname",
    },
}

BFT = {
    # Location of file uploads
    # Do not put a trailing slash!
    "FILE_UPLOAD_DIR": config("FILE_UPLOAD_DIR", default="files"),
    # Do not exceed 2 GB, your web server will not like you!
    # This used on the client (flash player) to enforce size limit
    "MAX_UPLOAD_SIZE": config("MAX_UPLOAD_SIZE", default=1610612736),  # 1.5GB
    # This setting is used my the management commands to
    # delete files.  Follow documentation to setup a cron job for this.
    "UPLOAD_EXPIRATION_DAYS": config("UPLOAD_EXPIRATION_DAYS", default=7),
    # General    "SERVER_NAME": config("SERVER_NAME", "localhost"),
    "APP_NAME": config("APP_NAME", default="Big File Transfer System"),
    "FROM_EMAIL": config("FROM_EMAIL", default="noreply@localhost"),
    "REPLY_EMAIL": config("REPLY_EMAIL", default="noreply@localhost"),
    "REPLY_EMAIL_NAME": config("REPLY_EMAIL_NAME", default="Big File Transfer System"),
    "SAML2_AUTHORITY": config("SAML2_AUTHORITY", default="SAML2"),
    # Slug generator    # This is used to randomize the file and file list urls
    "RANDOMSLUG_CHARS": config("RANDOMSLUG_CHARS", default="bcdfghjklmnpqrstvwxyz2346789"),
    "RANDOMSLUG_CHAR_NO": config("RANDOMSLUG_CHAR_NO", default=5),
}
