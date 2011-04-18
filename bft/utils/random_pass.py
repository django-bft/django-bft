from bft import app_settings
from random import choice

RANDOMPASS_CHARS = getattr(app_settings, "RANDOMPASS_CHARS", "bcdfghjklmnpqrstvwxyz2346789")
RANDOMPASS_CHAR_NO = getattr(app_settings, "RANDOMPASS_CHAR_NO", 8)

def get_random_pass():
	return ''.join([choice(RANDOMPASS_CHARS) for char in range(RANDOMPASS_CHAR_NO)])