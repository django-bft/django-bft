from datetime import datetime, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from sys import stdout
import os

class Command(BaseCommand):
	"""
	Cron Job that deletes clean up the temp files directory
	"""
	
	def handle(self, *args, **options):
		path = "%s/tmp/" % settings.BASE_DIR
	
		datediff = datetime.today() - timedelta(days=1)
	
		try:
			if os.path.isdir(path):
				
				files = os.listdir(path)
			
				for file in files:
					
					fullpath = os.path.join(path, file)
					
					if os.path.isfile(fullpath) and (datetime.fromtimestamp(os.path.getmtime(fullpath)) < datediff):
						os.remove(fullpath)
				
				stdout.write('Temp files have been deleted.\n')
	
		except:
			pass
