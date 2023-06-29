import os
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse

from .utils.random_slug import get_random_slug
from .validators import validate_type, validate_anumbers
from .app_settings import CONFIG as app_settings


class SubmissionManager(models.Manager):
    def get_expired_submissions(self):
        datediff = datetime.today() - timedelta(days=app_settings.UPLOAD_EXPIRATION_DAYS)
        submissions = Submission.objects.filter(submit_date__lte=datediff, is_archived=False)

        return submissions


class Submission(models.Model):
    type = models.CharField(validators=[validate_type], max_length=255)
    slug = models.SlugField(editable=False)
    email_address = models.EmailField(max_length=255)
    anumbers = models.TextField("A-numbers", validators=[validate_anumbers], blank=True)
    submit_ip = models.GenericIPAddressField(editable=False, blank=True, null=True)
    submit_date = models.DateTimeField(editable=False, auto_now_add=True)
    is_archived = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    browser_meta = models.CharField(max_length=255, editable=False, blank=True)

    objects = SubmissionManager()

    def __str__(self):
        return f"{self.id}"

    def save(self, *args, **kwargs):
        # make sure anumbers are lowercase
        if self.anumbers:
            anumbers = self.anumbers.lower()
            self.anumbers = anumbers

        # create a unique slug field
        if not self.pk:
            while True:
                slug = get_random_slug()
                if not Submission.objects.filter(slug=slug):
                    self.slug = slug
                    break
        super(Submission, self).save(*args, **kwargs)

    class Meta:
        app_label = "bft"


class Email(Submission):
    first_name = models.CharField("First Name", max_length=50)
    last_name = models.CharField("Last Name", max_length=50)
    recipients = models.TextField()
    message = models.TextField()

    def __str__(self):
        return f"{self.id}"

    class Meta:
        app_label = "bft"


class File(models.Model):
    submission = models.ForeignKey(Submission, null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(editable=False)
    file_upload = models.FileField(upload_to=app_settings.FILE_UPLOAD_DIR + "/%d-%m-%Y", max_length=500)
    file_size = models.DecimalField("File Size (MB)", editable=False, max_digits=8, decimal_places=3)

    def __str__(self):
        return f"{self.file_upload.name}"

    def save(self, *args, **kwargs):
        # get the size of the file and save it to file_size for the admin
        self.file_size = f"{(float(self.file_upload.size) / 1024 / 1024)}"

        # create a unique slug field
        if not self.pk:
            while True:
                slug = get_random_slug()
                if not File.objects.filter(slug=slug):
                    self.slug = slug
                    break
        super(File, self).save(*args, **kwargs)

    def delete(self):
        file_url = self.get_absolute_url()

        FileArchive.objects.create(
            submission=self.submission,
            file_upload=self.file_upload.url,
            submit_date=self.submission.submit_date,
        )
        super(File, self).delete()

        # fixes for django 1.3 since filefields dont auto delete files anymore.
        if os.path.isfile(file_url):
            os.remove(file_url)

    def was_saved(self):
        if self.pk:
            return True
        else:
            return False

    def get_short_url(self):
        return reverse("file", kwargs={"file_slug": self.slug})

    def get_absolute_url(self):
        return os.path.join(settings.BASE_DIR, settings.MEDIA_ROOT, self.file_upload.name)

    class Meta:
        app_label = "bft"


class FileArchive(models.Model):
    submission = models.ForeignKey(Submission, null=True, editable=False, on_delete=models.SET_NULL)
    file_upload = models.FilePathField(editable=False, max_length=500)
    submit_date = models.DateTimeField(editable=False)
    delete_date = models.DateTimeField(editable=False, auto_now_add=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        app_label = "bft"
