from django import forms
from django.contrib.auth import password_validation
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from allauth.account import app_settings
from allauth.account.adapter import get_adapter


class EmailField(forms.EmailField):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("label", _("Email"))
        kwargs.setdefault(
            "widget",
            forms.TextInput(
                attrs={
                    "type": "email",
                    "autocomplete": "email",
                    "placeholder": _("Email address"),
                }
            ),
        )
        super().__init__(*args, **kwargs)

    def clean(self, value):
        return super().clean(value).lower()


class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop(
            "render_value", app_settings.PASSWORD_INPUT_RENDER_VALUE
        )
        kwargs["widget"] = forms.PasswordInput(
            render_value=render_value,
            attrs={"placeholder": kwargs.get("label")},
        )
        autocomplete = kwargs.pop("autocomplete", None)
        if autocomplete is not None:
            kwargs["widget"].attrs["autocomplete"] = autocomplete
        super(PasswordField, self).__init__(*args, **kwargs)


class SetPasswordField(PasswordField):
    def __init__(self, *args, **kwargs):
        kwargs["autocomplete"] = "new-password"
        kwargs.setdefault(
            "help_text", password_validation.password_validators_help_text_html()
        )
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self, value):
        value = super().clean(value)
        value = get_adapter().clean_password(value, user=self.user)
        return value


class PhoneField(forms.CharField):
    e164_validator = RegexValidator(
        regex=r"^\+[1-9]\d{5,14}$",
        message=_("Enter a phone number including country code (e.g. +1 for the US)."),
        code="invalid_phone",
    )

    def __init__(self, *args, **kwargs):
        widget = forms.TextInput(
            attrs={"placeholder": _("Phone"), "autocomplete": "tel", "type": "tel"}
        )
        kwargs.setdefault("validators", [self.e164_validator])
        kwargs.setdefault("widget", widget)
        kwargs.setdefault("label", _("Phone"))
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        if value:
            value = value.replace(" ", "").replace("-", "")
            value = get_adapter().clean_phone(value)
        return value
