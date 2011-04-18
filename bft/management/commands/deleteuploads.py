from bft.app_settings import APP_NAME
from bft.models import Submission, File
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from optparse import make_option
from sys import stdout

class Command(BaseCommand):
	"""
	Cron Job that checks uploads that are past the expiration period and removes them from the system.
	"""
	
	option_list = BaseCommand.option_list + (
        make_option('--mailadmins', '-M', dest='mailadmins', default=None,
            help='Use this option to email admins of any files that were deleted.'),
    )
	
	def handle(self, *args, **options):
		deleted_files = []
		
		submissions = Submission.objects.get_expired_submissions()
		
		for submission in submissions:
			files = File.objects.filter(submission=submission)
	
			for file in files:
				deleted_files.append(file.file_upload.url)
				file.delete()
			
			submission.is_archived = True
			submission.save()
			
		message = '''
The following files have expired and deleted:
	
'''
		if deleted_files:
			body = "%s%s" % (message, '\n'.join(file for file in deleted_files))

			if options['mailadmins']:		
				mail_admins('[%s] File cleanup summary' % APP_NAME, body)
			
			stdout.write(body + '\n')
		else:
			stdout.write('No expired files were deleted.\n')
