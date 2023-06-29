from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .forms import EmailForm, FileForm, SubmissionForm
from .models import Submission, Email, File, FileArchive
import os


def delete_row(obj):
    return mark_safe(f'<a href="{obj.id}/delete">Delete</a>')


delete_row.allow_tags = True
delete_row.short_description = "Delete"


def edit_row(obj):
    return mark_safe(f'<a href="{obj.id}">Edit</a>')


edit_row.short_description = "Edit"


def file_url(obj):
    url = reverse("file", args=(obj.slug,))
    return mark_safe(f'<a href="{url}">{url}</a>')


file_url.short_description = "File URL"


def submission_url(obj):
    url = reverse("files", args=(obj.slug,))
    return mark_safe(f'<a href="{url}">{url}</a>')


submission_url.short_description = "Submission URL"


def submission_admin_url(obj):
    url = reverse("admin:bft_submission_change", args=(obj.submission,))
    return mark_safe(f'<a href="{url}">{obj.submission}</a>')


submission_admin_url.short_description = "Submission"


def attached_files(obj):
    files = File.objects.filter(submission=obj.id)
    if files:
        file_list = []
        for file in files:
            file_list.append(f'<a href="/{file.slug}/{os.path.basename(file.file_upload.name)}">{file.slug}</a>')
        return mark_safe(" ".join(file_list))
    else:
        return None


def attached_submission_date(obj):
    return obj.submission.submit_date if obj.submission else None


attached_submission_date.short_description = "Upload Date"


class EmailInline(admin.StackedInline):
    model = Email
    form = EmailForm
    fields = ("first_name", "last_name", "recipients", "message")


class FileInline(admin.StackedInline):
    model = File
    form = FileForm
    extra = 3


class SubmissionAdmin(admin.ModelAdmin):
    list_filter = ("type", "submit_date")
    search_fields = [
        "email_address",
        "slug",
        "submit_ip",
        "file__slug",
        "email__recipients",
    ]
    fields = ("type", "email_address", "anumbers", "is_archived", "email_sent")
    list_display = (
        "id",
        submission_url,
        "type",
        "email_address",
        attached_files,
        "submit_date",
        "submit_ip",
        "browser_meta",
        delete_row,
        edit_row,
    )
    inlines = [EmailInline, FileInline]
    form = SubmissionForm

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        submission = form.save(commit=False)
        submission.submit_ip = request.META["REMOTE_ADDR"]
        for instance in instances:
            instance.submit_ip = request.META["REMOTE_ADDR"]
            instance.save()
        submission.save()

    def save_model(self, request, obj, form, change):
        obj.submit_ip = request.META["REMOTE_ADDR"]
        obj.save()


class FileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        file_url,
        submission_admin_url,
        "file_upload",
        "file_size",
        attached_submission_date,
        delete_row,
        edit_row,
    )
    search_fields = [
        "file_upload",
        "slug",
        "submission__pk",
        "submission__email_address",
    ]

    form = FileForm


class FileArchiveAdmin(admin.ModelAdmin):
    list_display = (
        "delete_date",
        "submit_date",
        submission_admin_url,
        "file_upload",
        delete_row,
    )

    list_filter = ("submit_date", "delete_date")
    search_fields = ["file_upload", "submission__pk"]


admin.site.register(Submission, SubmissionAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(FileArchive, FileArchiveAdmin)
