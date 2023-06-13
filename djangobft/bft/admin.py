from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
    return mark_safe(f'<a href="{url}{os.path.basename(obj.file_upload.name)}">{url}</a>')


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
        return " ".join(mark_safe(file_list))
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
    class Media:
        js = (
            "https://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js",
            "/static/scripts/admin.js",
        )

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


# Override of User Creation Form to check for USU A-numbers
class ExternalUserCreationForm(UserCreationForm):
    is_usu_credential = forms.BooleanField(
        label=_("Is USU A-Number"),
        initial=False,
        required=False,
        help_text=_("Check if this user is a USU A-Number so that local passwords will not be used."),
    )

    def _is_usu_user(self):
        result = False
        if ("is_usu_credential") in self.cleaned_data:
            if ("username") in self.cleaned_data:
                self.cleaned_data["username"] = self.cleaned_data["username"]
            result = self.cleaned_data["is_usu_credential"]
        return result

    def clean_username(self):
        username = super(ExternalUserCreationForm, self).clean_username()
        return username.upper()

    def clean(self):
        cleaned_data = super(ExternalUserCreationForm, self).clean()
        # Ignore password errors if we aren't using the password field
        if self._is_usu_user():
            if ("password1") in self.errors:
                del self.errors["password1"]
            if ("password1") in self.errors:
                del self.errors["password2"]
        return cleaned_data

    def save(self, commit=True):
        if self._is_usu_user():
            user = super(UserCreationForm, self).save(commit=False)
            user.set_unusable_password()
            if commit:
                user.save()
        else:
            user = super(ExternalUserCreationForm, self).save(commit=commit)
        return user


class ExtendedUserAdmin(UserAdmin):
    # add_form_template = 'admin/auth/user/add_user.html'
    add_form = ExternalUserCreationForm

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "is_usu_credential"),
            },
        ),
    )


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(File, FileAdmin)
admin.site.register(FileArchive, FileArchiveAdmin)
