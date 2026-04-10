from __future__ import annotations

from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.mfa.adapter import get_adapter
from allauth.mfa.internal.flows.add import validate_can_add_authenticator
from allauth.mfa.totp.internal import auth


class ActivateTOTPForm(forms.Form):
    code = forms.CharField(
        label=_("Authenticator code"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "one-time-code"},
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.secret = auth.get_totp_secret(regenerate=not self.is_bound)

    def clean_code(self) -> str:
        validate_can_add_authenticator(self.user)
        code = self.cleaned_data["code"]
        if not auth.validate_totp_code(self.secret, code):
            raise get_adapter().validation_error("incorrect_code")
        return code


class DeactivateTOTPForm(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        self.authenticator = kwargs.pop("authenticator")
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        adapter = get_adapter()
        if not adapter.can_delete_authenticator(self.authenticator):
            raise adapter.validation_error("cannot_delete_authenticator")
        return cleaned_data
