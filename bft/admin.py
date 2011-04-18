import app_settings
from django.core.urlresolvers import reverse
from django.contrib import admin
from forms import EmailForm, FileForm, SubmissionForm
from models import Submission, Email, File, FileArchive
import os

#global callables
def delete_row(obj):
	return '<a href="%s/delete">Delete</a>' % obj.id
delete_row.allow_tags = True
delete_row.short_description = 'Delete'

def edit_row(obj):
	return '<a href="%s">Edit</a>' % obj.id
edit_row.short_description = 'Edit'
edit_row.allow_tags = True

def file_url(obj):
	url = reverse('file', args=(obj.slug,))
	return '<a href="%s%s">%s</a>' % (url, os.path.basename(obj.file_upload.name), url)
file_url.short_description = 'File URL'
file_url.allow_tags = True

def submission_url(obj):
	url = reverse('files', args=(obj.slug,))
	return '<a href="%s">%s</a>' % (url, url)
submission_url.short_description = 'Submission URL'
submission_url.allow_tags = True

def submission_admin_url(obj):
	url = reverse('admin:bft_submission_change', args=(obj.submission,))
	return '<a href="%s">%s</a>' % (url, obj.submission)
submission_admin_url.short_description = 'Submission'
submission_admin_url.allow_tags = True

def attached_files(obj):
	files = File.objects.filter(submission=obj.id)
	if files:
		file_list = []
		for file in files:
			file_list.append('<a href="/%s/%s">%s</a>' % (file.slug, 
						os.path.basename(file.file_upload.name), file.slug))
		return ' '.join(file_list)
	else:
		return None
attached_files.allow_tags = True

def attached_submission_date(obj):
	return obj.submission.submit_date
attached_submission_date.short_description = 'Upload Date'

def submission_fields():
	if app_settings.RANDOM_PASS:
		return ('type', 'email_address', 'is_archived', 'email_sent')
	else:
		return ('type', 'email_address', 'password', 'is_archived', 'email_sent')
		

#inlines
class EmailInline(admin.StackedInline):
	model = Email
	form = EmailForm
	fields = ('first_name', 'last_name', 'recipients', 'message')
	
class FileInline(admin.StackedInline):
	model = File
	form = FileForm
	extra = 3
	
#admin views
class SubmissionAdmin(admin.ModelAdmin):
	class Media:
		js = (
			'https://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js',
			'/static/scripts/admin.js',
		)
	
	list_filter = ('type', 'submit_date')
	search_fields = ['email_address', 'slug', 'submit_ip', 'file__slug', 'email__recipients']
	fields = submission_fields()
	list_display = ('id', submission_url, 'type', 'email_address', 'password', 
		attached_files, 'submit_date', 'submit_ip', 'browser_meta', delete_row, edit_row)
	inlines = [EmailInline, FileInline]
	form = SubmissionForm
	
	def save_model(self, request, obj, form, change):
		obj.submit_ip = request.META['REMOTE_ADDR']
		obj.save()


class FileAdmin(admin.ModelAdmin):
	list_display = ('id', file_url, submission_admin_url, 'file_upload', 
		'file_size', attached_submission_date, delete_row, edit_row)
	search_fields = ['file_upload', 'slug', 'submission__pk', 'submission__email_address']
	
	form = FileForm

class FileArchiveAdmin(admin.ModelAdmin):
	list_display = ('delete_date', 'submit_date', submission_admin_url, 'file_upload', delete_row)
	
	list_filter = ('submit_date', 'delete_date')
	search_fields = ['file_upload', 'submission__pk']

admin.site.register(Submission, SubmissionAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(FileArchive, FileArchiveAdmin)
