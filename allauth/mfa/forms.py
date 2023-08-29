from django import forms
from django.core.signing import BadSignature, Signer
from django.utils.translation import gettext_lazy as _

from allauth.account.models import EmailAddress
from allauth.mfa import totp
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator


class AuthenticateForm(forms.Form):
    code = forms.CharField(label=_("Code"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"]
        for auth in Authenticator.objects.filter(user=self.user):
            if auth.wrap().validate_code(code):
                self.authenticator = auth
                return code
        raise forms.ValidationError(get_adapter().error_messages["incorrect_code"])


class ActivateTOTPForm(forms.Form):
    signed_secret = forms.CharField(widget=forms.HiddenInput)
    code = forms.CharField(label=_("Authenticator code"))

    def __init__(self, *args, **kwargs):
        initial = kwargs.setdefault("initial", {})
        self.user = kwargs.pop("user")
        initial["signed_secret"] = Signer().sign(totp.totp_secret())
        self.email_verified = not EmailAddress.objects.filter(
            user=self.user, verified=False
        ).exists()
        super().__init__(*args, **kwargs)

    @property
    def secret(self):
        signed_secret = (
            self.data.get("signed_secret")
            if self.is_bound
            else self.initial["signed_secret"]
        )
        try:
            return Signer().unsign(signed_secret)
        except BadSignature:
            # Don't care -- somebody tampered with the form
            return "tampered"

    def clean_signed_secret(self):
        signed_secret = self.cleaned_data["signed_secret"]
        try:
            return Signer().unsign(signed_secret)
        except BadSignature:
            raise forms.ValidationError("Tampered form.")

    def clean(self):
        cleaned_data = super().clean()
        secret = cleaned_data.get("signed_secret")
        code = cleaned_data.get("code")

        if not self.email_verified:
            raise forms.ValidationError(
                get_adapter().error_messages["unverified_email"]
            )

        if secret and code:
            if not totp.validate_totp_code(secret, code):
                self.add_error("code", get_adapter().error_messages["incorrect_code"])

        return cleaned_data
