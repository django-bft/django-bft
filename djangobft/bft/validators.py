from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
import ast


def validate_type(value):
    if value != "email" and value != "link":
        raise ValidationError('The Submission type needs to be "link" or "email".')


def validate_recipients(value):
    list(value.split(","))
    for email in value:
        if email:
            try:
                validate_email(email.strip())
            except ValidationError:
                raise "At least one of the emails for the recipients is not valid."


def validate_anumbers(value):
    value_list = ast.literal_eval(value)
    for anumber in value_list:
        if anumber:
            if anumber.lower().startswith("a") and re.match("^\d{8}$", anumber.lower().split("a")[1]):
                pass
            else:
                raise ValidationError("At least one of the A-numbers provided is not valid.")
