from ...app_settings import CONFIG as app_settings
from ...models import Submission, File
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from sys import stdout
import os


class Command(BaseCommand):
    """
    Cron Job that checks uploads that are past the expiration period and removes them from the system.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--mailadmins",
            "-M",
            action="store_true",
            help="Use this option to email admins of any files that were deleted.",
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

        # Clean up empty directories
        files_dir = os.listdir(settings.MEDIA_ROOT + app_settings.FILE_UPLOAD_DIR)
        date_dir = (datetime.today() - timedelta(days=app_settings.UPLOAD_EXPIRATION_DAYS)).strftime("%d-%m-%Y")

        for dir in files_dir:
            if dir != date_dir:
                dir_temp = settings.MEDIA_ROOT + app_settings.FILE_UPLOAD_DIR + "/" + dir
                if not os.listdir(dir_temp):
                    os.rmdir(dir_temp)
                    stdout.write("Empty directory %s was deleted.\n" % dir_temp)

        if deleted_files:
            message = """
The following files have expired and deleted:

					"""
            body = "%s%s" % (message, "\n".join(file for file in deleted_files))

            if options["mailadmins"]:
                mail_admins("[%s] File cleanup summary" % APP_NAME, body)

            stdout.write(body + "\n")
        else:
            stdout.write("No expired files were deleted.\n")
