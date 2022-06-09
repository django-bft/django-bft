from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re

def validate_type(value):
	if value != 'email' and value != 'link':
		raise ValidationError(u'The Submission type needs to be "link" or "email".')
	
def validate_recipients(value):
	value_list = re.split("[:;, ]", value)
	for email in value_list:
		if email:
			try:
				validate_email(email.strip())
			except:
				raise ValidationError(u'At least one of the emails for the recipients is not valid.')

def validate_anumbers(value):
	value_list = re.split("[:;, ]", value)
	for anumber in value_list:
		if anumber:
			if anumber.lower().startswith('a') and re.match("^\d{8}$", anumber.lower().split('a')[1]):
				pass
			else:
				raise ValidationError(u'At least one of the A-numbers provided is not valid.')
