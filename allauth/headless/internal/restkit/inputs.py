from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    Field,
    Form,
    ModelChoiceField,
    ModelMultipleChoiceField,
)

from allauth.account.fields import EmailField


__all__ = [
    "Field",
    "CharField",
    "ChoiceField",
    "EmailField",
    "BooleanField",
    "ModelMultipleChoiceField",
    "ModelChoiceField",
]


class Input(Form):
    pass
