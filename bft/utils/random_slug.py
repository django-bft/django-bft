from bft import app_settings
from random import choice

RANDOMSLUG_CHARS = getattr(app_settings, "RANDOMSLUG_CHARS", "bcdfghjklmnpqrstvwxyz2346789")
RANDOMSLUG_CHAR_NO = getattr(app_settings, "RANDOMSLUG_CHAR_NO", 5)

def get_random_slug():
	return ''.join([choice(RANDOMSLUG_CHARS) for char in range(RANDOMSLUG_CHAR_NO)])