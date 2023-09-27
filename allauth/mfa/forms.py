import json

from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.models import EmailAddress
from allauth.core import context, ratelimit
from allauth.mfa import totp
from allauth.mfa.adapter import get_adapter
from allauth.mfa.internal import flows
from allauth.mfa.models import Authenticator
from allauth.mfa.utils import post_authentication
from allauth.mfa.webauthn import (
    begin_authentication,
    begin_registration,
    complete_authentication,
    complete_registration,
    parse_authentication_credential,
    parse_registration_credential,
)


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
        for auth in Authenticator.objects.filter(user=self.user).exclude(
            type=Authenticator.Type.WEBAUTHN
        ):
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


class AuthenticateWebAuthnForm(forms.Form):
    credential = forms.CharField(required=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.authentication_data = begin_authentication(self.user)
        super().__init__(*args, **kwargs)

    def clean_credential(self):
        credential = self.cleaned_data["credential"]
        user, credential = parse_authentication_credential(json.loads(credential))
        # FIXME: Raise form error
        assert user is None or self.user.pk == user.pk
        return complete_authentication(self.user, credential)

    def save(self):
        authenticator = self.cleaned_data["credential"]
        authenticator.record_usage()


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


class AddWebAuthnForm(forms.Form):
    name = forms.CharField(required=False)
    passwordless = forms.BooleanField(
        label=_("Passwordless"),
        required=False,
        help_text=_(
            "Enabling passwordless operation allows you to sign in using just this key/device, but imposes additional requirements such as biometrics or PIN protection."
        ),
    )
    credential = forms.CharField(required=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.registration_data = begin_registration(self.user)
        super().__init__(*args, **kwargs)

    def clean_credential(self):
        credential = self.cleaned_data["credential"]
        return parse_registration_credential(json.loads(credential))

    def clean(self):
        cleaned_data = super().clean()
        credential = cleaned_data.get("credential")
        passwordless = cleaned_data.get("passwordless")
        if credential:
            if (
                passwordless
                and not credential["attestation_object"].auth_data.is_user_verified()
            ):
                self.add_error(
                    None, _("This key does not support passwordless operation.")
                )
            else:
                cleaned_data["authenticator_data"] = complete_registration(credential)
        return cleaned_data
