from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.core import context, ratelimit
from allauth.mfa import totp
from allauth.mfa.adapter import get_adapter
from allauth.mfa.internal import flows
from allauth.mfa.models import Authenticator


class BaseAuthenticateForm(forms.Form):
    code = forms.CharField(
        label=_("Code"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "one-time-code"},
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_code(self):
        key = f"mfa-auth-user-{str(self.user.pk)}"
        if not ratelimit.consume(
            context.request,
            action="login_failed",
            key=key,
        ):
            raise get_account_adapter().validation_error("too_many_login_attempts")

        code = self.cleaned_data["code"]
        for auth in Authenticator.objects.filter(user=self.user):
            if auth.wrap().validate_code(code):
                self.authenticator = auth
                ratelimit.clear(context.request, action="login_failed", key=key)
                return code

        raise get_adapter().validation_error("incorrect_code")


class AuthenticateForm(BaseAuthenticateForm):
    def save(self):
        flows.authentication.post_authentication(context.request, self.authenticator)


class ReauthenticateForm(BaseAuthenticateForm):
    def save(self):
        flows.authentication.post_authentication(
            context.request, self.authenticator, reauthenticated=True
        )


class ActivateTOTPForm(forms.Form):
    code = forms.CharField(
        label=_("Authenticator code"),
        widget=forms.TextInput(
            attrs={"placeholder": _("Code"), "autocomplete": "one-time-code"},
        ),
    )

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
                raise get_adapter().validation_error("unverified_email")
            if not totp.validate_totp_code(self.secret, code):
                raise get_adapter().validation_error("incorrect_code")
            return code
        except forms.ValidationError as e:
            raise e


class DeactivateTOTPForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.authenticator = kwargs.pop("authenticator")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        adapter = get_adapter()
        if not adapter.can_delete_authenticator(self.authenticator):
            raise adapter.validation_error("cannot_delete_authenticator")
        return cleaned_data


class GenerateRecoveryCodesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if not flows.recovery_codes.can_generate_recovery_codes(self.user):
            raise get_adapter().validation_error("cannot_generate_recovery_codes")
        return cleaned_data
