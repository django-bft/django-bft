from django import forms
from .models import Email, File, Submission
import django.forms.fields as fields
import django.forms.widgets as widgets

from django.core.exceptions import ValidationError

TYPE_CHOICES = (
    ("link", "Link"),
    ("email", "Email"),
)


class MultiValueValidationError(ValidationError):
    def __init__(self, errors):
        clean_errors = [f"{message} (item {key})" for message, key, value in errors]
        super().__init__(clean_errors)
        self.error_detail = errors


class MultiValueFieldWidget(widgets.Input):
    def __init__(self, param_name: str) -> None:
        super().__init__()
        self.param_name: str = param_name

    def value_from_datadict(self, data, *args):
        return data.getlist(self.param_name)


class MultiValueField(fields.Field):
    def __init__(self, subfield: fields.Field, param_name: str, *args, **kwargs) -> None:
        super().__init__(
            widget=MultiValueFieldWidget(param_name),
            *args,
            **kwargs,
        )
        self.error_messages["required"] = "Please specify one or more '{}' arguments.".format(param_name)
        self.subfield = subfield

    def clean(self, values):
        if len(values) == 0 and self.required:
            raise ValidationError(self.error_messages["required"])
        result = []
        errors = []
        for i, value in enumerate(values):
            try:
                result.append(self.subfield.clean(value))
            except ValidationError as e:
                errors.append((e.message, i, value))
        if len(errors):
            raise MultiValueValidationError(errors)
        return result


class EmailForm(forms.ModelForm):
    first_name = forms.CharField(error_messages={"required": "Please enter your first name."})
    last_name = forms.CharField(error_messages={"required": "Please enter your last name."})
    recipients = MultiValueField(
        forms.CharField(
            error_messages={"required": "Please enter the recipient(s) email separated by commas."},
            widget=forms.Textarea,
            help_text="Enter a set of email addresses separated by commas",
        ),
        "recipients",
    )
    anumbers = MultiValueField(
        forms.CharField(
            widget=forms.Textarea,
            help_text="Enter a set of A-numbers separated by commas",
            required=False,
        ),
        "anumbers",
    )
    message = forms.CharField(error_messages={"required": "Please enter a message."}, widget=forms.Textarea)

    class Meta:
        exclude = ("submission",)
        model = Email


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = "__all__"


class SubmissionForm(forms.ModelForm):
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    email_address = forms.CharField(error_messages={"required": "Please enter a valid email address."})

    class Meta:
        model = Submission
        fields = "__all__"
