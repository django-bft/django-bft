from django.conf import settings

from collections import namedtuple

CONFIG_DEFAULTS = {
    # Location of file uploads
    # Do not put a trailing slash!
    "FILE_UPLOAD_DIR": getattr(settings, "FILE_UPLOAD_DIR", "files"),
    # Do not exceed 2 GB, your web server will not like you!
    # This used on the client (flash player) to enforce size limit
    "MAX_UPLOAD_SIZE": getattr(settings, "MAX_UPLOAD_SIZE", 1610612736),  # 1.5GB
    # This setting is used my the management commands to
    # delete files.  Follow documentation to setup a cron job for this.
    "UPLOAD_EXPIRATION_DAYS": getattr(settings, "UPLOAD_EXPIRATION_DAYS", 7),
    # General settings
    "SERVER_NAME": getattr(settings, "SERVER_NAME", "localhost"),
    "APP_NAME": getattr(settings, "APP_NAME", "Big File Transfer System"),
    "REPLY_EMAIL": getattr(settings, "REPLY_EMAIL", "bft@localhost"),
    "SAML2_AUTHORITY": getattr(settings, "SAML2_AUTHORITY", "SAML2"),
    # Slug generator settings
    # This is used to randomize the file and file list urls
    "RANDOMSLUG_CHARS": getattr(settings, "RANDOMSLUG_CHARS", "bcdfghjklmnpqrstvwxyz2346789"),
    "RANDOMSLUG_CHAR_NO": getattr(settings, "RANDOMSLUG_CHAR_NO", 5),
}


BFT_CONFIG = getattr(settings, "BFT", {})
CONFIG = CONFIG_DEFAULTS.copy()
CONFIG.update(BFT_CONFIG)
CONFIG = namedtuple("CONFIG", CONFIG.keys())(*CONFIG.values())
