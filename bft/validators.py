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