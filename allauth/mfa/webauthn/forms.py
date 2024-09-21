from django import forms
from django.utils.translation import gettext_lazy as _

from allauth.core import context
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.base.internal.flows import (
    check_rate_limit,
    post_authentication,
)
from allauth.mfa.models import Authenticator
from allauth.mfa.webauthn.internal import auth, flows


class _BaseAddWebAuthnForm(forms.Form):
    name = forms.CharField(required=False)
    credential = forms.JSONField(required=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        initial = kwargs.setdefault("initial", {})
        initial.setdefault(
            "name",
            get_adapter().generate_authenticator_name(
                self.user, Authenticator.Type.WEBAUTHN
            ),
        )
        super().__init__(*args, **kwargs)

    def clean_name(self):
        """
        We don't want to make `name` a required field, as the WebAuthn
        ceremony happens before posting the resulting credential, and we don't
        want to reject a valid credential because of a missing name -- it might
        be resident already. So, gracefully plug in a name.
        """
        name = self.cleaned_data["name"]
        if not name:
            name = get_adapter().generate_authenticator_name(
                self.user, Authenticator.Type.WEBAUTHN
            )
        return name

    def clean(self):
        cleaned_data = super().clean()
        credential = cleaned_data.get("credential")
        if credential:
            # Explicitly parse JSON payload -- otherwise, register_complete()
            # crashes with some random TypeError and we don't want to do
            # Pokemon-style exception handling.
            auth.parse_registration_response(credential)
            auth.complete_registration(credential)
        return cleaned_data


class AddWebAuthnForm(_BaseAddWebAuthnForm):
    if app_settings.PASSKEY_LOGIN_ENABLED:
        passwordless = forms.BooleanField(
            label=_("Passwordless"),
            required=False,
            help_text=_(
                "Enabling passwordless operation allows you to sign in using just this key, but imposes additional requirements such as biometrics or PIN protection."
            ),
        )


class SignupWebAuthnForm(_BaseAddWebAuthnForm):
    pass


class AuthenticateWebAuthnForm(forms.Form):
    credential = forms.JSONField(required=True, widget=forms.HiddenInput)
    reauthenticated = False
    passwordless = False

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean_credential(self):
        credential = self.cleaned_data["credential"]
        # Explicitly parse JSON payload -- otherwise, authenticate_complete()
        # crashes with some random TypeError and we don't want to do
        # Pokemon-style exception handling.
        auth.parse_authentication_response(credential)
        user = self.user
        if user is None:
            user = auth.extract_user_from_response(credential)
        clear_rl = check_rate_limit(user)
        authenticator = auth.complete_authentication(user, credential)
        clear_rl()
        return authenticator

    def save(self):
        authenticator = self.cleaned_data["credential"]
        post_authentication(
            context.request,
            authenticator,
            reauthenticated=self.reauthenticated,
            passwordless=self.passwordless,
        )


class LoginWebAuthnForm(AuthenticateWebAuthnForm):
    reauthenticated = False
    passwordless = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, user=None, **kwargs)


class ReauthenticateWebAuthnForm(AuthenticateWebAuthnForm):
    reauthenticated = True
    passwordless = False


class EditWebAuthnForm(forms.Form):
    name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop("instance")
        initial = kwargs.setdefault("initial", {})
        initial.setdefault("name", self.instance.wrap().name)
        super().__init__(*args, **kwargs)

    def save(self) -> Authenticator:
        flows.rename_authenticator(
            context.request, self.instance, self.cleaned_data["name"]
        )
        return self.instance
