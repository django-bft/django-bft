# Location of file uploads relative to MEDIA_ROOT
# Do not put a trailing slash!
FILE_UPLOAD_DIR = "files"

# Do not exceed 2 GB, your web server will not like you!
# This used on the client (flash player) to enforce size limit
MAX_UPLOAD_SIZE = 1073741824  # 1GB

# This setting is used my the management commands to
# delete files.  Follow documentation to setup a cron job for this.
UPLOAD_EXPIRATION_DAYS = 7


# !! -- NOT EXACTLY SURE IF THIS IS NEEDED -- !!

# Set to have Django try to enforce MAX_UPLOAD_SIZE
# It is far better to enforce this using the web server (Apache)
# An example would be:
# LimitRequestBody 1073741824
# ErrorDocument 413 http://servername/413error/
VALIDATE_UPLOAD_SIZE = True

# General settings
APP_NAME = "USU's Big File Transfer System"
REPLY_EMAIL = "pad@usu.edu"

# A list of subnets to not include in captcha
# Example:  ['172.17', "10.10']
CAPTCHA_SUBNET_EXCLUDE = ["129.123", "172.17", "144.39"]

CAPTCHA_CHALLENGE_URL = "https://verifyme.usu.edu/challenge/"
CAPTCHA_VERIFY_URL = "https://verifyme.usu.edu/verify/"

# Slug generator settings
# This is used to randomize the file and file list urls
RANDOMSLUG_CHARS = "bcdfghjklmnpqrstvwxyz2346789"
RANDOMSLUG_CHAR_NO = 5
