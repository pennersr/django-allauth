from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.core import context, ratelimit
from allauth.mfa import totp
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator


class AuthenticateForm(forms.Form):
    code = forms.CharField(
        label=_("Code"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "off"},
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_code(self):
        if account_settings.LOGIN_ATTEMPTS_LIMIT:
            if not ratelimit.consume(
                context.request,
                action="login_failed",
                user=self.user,
                amount=account_settings.LOGIN_ATTEMPTS_LIMIT,
                duration=account_settings.LOGIN_ATTEMPTS_TIMEOUT,
            ):
                raise forms.ValidationError(
                    get_account_adapter().error_messages["too_many_login_attempts"]
                )

        code = self.cleaned_data["code"]
        for auth in Authenticator.objects.filter(user=self.user):
            if auth.wrap().validate_code(code):
                self.authenticator = auth
                ratelimit.clear(context.request, action="login_failed", user=self.user)
                return code
        raise forms.ValidationError(get_adapter().error_messages["incorrect_code"])


class ActivateTOTPForm(forms.Form):
    code = forms.CharField(label=_("Authenticator code"))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.email_verified = not EmailAddress.objects.filter(
            user=self.user, verified=False
        ).exists()
        super().__init__(*args, **kwargs)
        self.secret = totp.get_totp_secret(regenerate=not self.is_bound)

    def clean_code(self):
        try:
            code = self.cleaned_data["code"]
            if not self.email_verified:
                raise forms.ValidationError(
                    get_adapter().error_messages["unverified_email"]
                )
            if not totp.validate_totp_code(self.secret, code):
                raise forms.ValidationError(
                    get_adapter().error_messages["incorrect_code"]
                )
            return code
        except forms.ValidationError as e:
            self.secret = totp.get_totp_secret(regenerate=True)
            raise e
