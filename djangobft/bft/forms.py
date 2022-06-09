from django import forms
from models import Email, File, Submission

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
	anumbers = forms.CharField(
		widget=forms.Textarea,
		help_text="Enter a set of A-numbers separated by commas",
		required=False
	)
	message = forms.CharField(error_messages={'required':'Please enter a message.'}, widget=forms.Textarea)
	
	class Meta:
		model = Email
		
class FileForm(forms.ModelForm):
	class Meta:
		model = File

class SubmissionForm(forms.ModelForm):
	type = forms.ChoiceField(choices=TYPE_CHOICES)
	email_address = forms.CharField(error_messages={'required':'Please enter a valid email address.'})
	
	class Meta:
		model = Submission
	
