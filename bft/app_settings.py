# Location of file uploads relative to MEDIA_ROOT
# Do not put a trailing slash!
FILE_UPLOAD_DIR = 'files'

# Do not exceed 2 GB, your web server will not like you!
# This used on the client (flash player) to enforce size limit
MAX_UPLOAD_SIZE = 1073741824 #1GB

# This setting is used my the management commands to 
# delete files.  Follow documentation to setup a cron job for this.
UPLOAD_EXPIRATION_DAYS = 7

# Set to have Django try to enforce MAX_UPLOAD_SIZE
# It is far better to enforce this using the web server (Apache)
# An example would be:
# LimitRequestBody 1073741824
# ErrorDocument 413 http://servername/413error/ 
VALIDATE_UPLOAD_SIZE = True

# Feedback form
SHOW_FEEDBACK = True

# General settings
APP_NAME = 'BFT'
REPLY_EMAIL = ''
USE_FLASH = True

# Captcha settings
USE_RECAPTCHA = False
# A list of subnets to not include in captcha
# Example:  ['172.17', 10.10']
RECAPTCHA_SUBNET = []
RECAPTCHA_PUB_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

# Slug generator settings
# This is used to randomize the file and file list urls
RANDOMSLUG_CHARS = "bcdfghjklmnpqrstvwxyz2346789"
RANDOMSLUG_CHAR_NO = 5

# If used, then passwords will not be encrypted regardless.
RANDOM_PASS = False

# Use this to encrypt non random passwords
# RANDOM_PASS must be False for this to work.
ENCRYPT_PASS = True

# Used to generate a random password
RANDOMPASS_CHARS = 'bcdfghjklmnpqrstvwxyz2346789'
RANDOMPASS_CHAR_NO = 8


