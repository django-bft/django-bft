from django import forms
from models import Email, File, Submission
from bft.app_settings import RANDOMPASS_CHAR_NO

TYPE_CHOICES = (
	('link', 'Link'),
	('email', 'Email'),
)

class EmailForm(forms.ModelForm):
	first_name = forms.CharField(error_messages={'required':'Please enter your first name.'})
	last_name = forms.CharField(error_messages={'required':'Please enter your last name.'})
	recipients = forms.CharField(
		error_messages={'required':'Please enter the recipient(s) email separated by commas.'},
		widget=forms.Textarea,
		help_text="Enter a set of email addresses separated by commas"
	)
	message = forms.CharField(error_messages={'required':'Please enter a message.'}, widget=forms.Textarea)
	
	class Meta:
		exclude = ('submission',)
		model = Email
		
class FileForm(forms.ModelForm):
	class Meta:
		model = File

class SubmissionForm(forms.ModelForm):
	type = forms.ChoiceField(choices=TYPE_CHOICES)
	email_address = forms.CharField(error_messages={'required':'Please enter a valid email address.'})
	password = forms.CharField(
		error_messages={'min_length':'Please ensure that your password is at least 8 characters in length.'},
		widget = forms.PasswordInput,
		min_length = RANDOMPASS_CHAR_NO,
		help_text = "Enter a password that contains at least 8 characters.",
		required = False
	)
	
	class Meta:
		model = Submission
	
