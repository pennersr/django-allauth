from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    EmailField,
    Field,
    Form,
    ModelMultipleChoiceField,
)


__all__ = [
    "Field",
    "CharField",
    "ChoiceField",
    "EmailField",
    "BooleanField",
    "ModelMultipleChoiceField",
]


class Input(Form):
    pass
