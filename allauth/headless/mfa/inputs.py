from allauth.account.forms import BaseSignupForm
from allauth.headless.internal.restkit import inputs
from allauth.mfa.base.forms import AuthenticateForm
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.forms import GenerateRecoveryCodesForm
from allauth.mfa.totp.forms import ActivateTOTPForm
from allauth.mfa.webauthn.forms import (
    AddWebAuthnForm,
    AuthenticateWebAuthnForm,
    LoginWebAuthnForm,
    ReauthenticateWebAuthnForm,
    SignupWebAuthnForm,
)


class AuthenticateInput(AuthenticateForm, inputs.Input):
    pass


class ActivateTOTPInput(ActivateTOTPForm, inputs.Input):
    pass


class GenerateRecoveryCodesInput(GenerateRecoveryCodesForm, inputs.Input):
    pass


class AddWebAuthnInput(AddWebAuthnForm, inputs.Input):
    pass


class CreateWebAuthnInput(SignupWebAuthnForm, inputs.Input):
    pass


class UpdateWebAuthnInput(inputs.Input):
    id = inputs.ModelChoiceField(queryset=Authenticator.objects.none())
    name = inputs.CharField(required=True, max_length=100)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["id"].queryset = Authenticator.objects.filter(
            user=self.user, type=Authenticator.Type.WEBAUTHN
        )


class DeleteWebAuthnInput(inputs.Input):
    authenticators = inputs.ModelMultipleChoiceField(
        queryset=Authenticator.objects.none()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["authenticators"].queryset = Authenticator.objects.filter(
            user=self.user, type=Authenticator.Type.WEBAUTHN
        )


class ReauthenticateWebAuthnInput(ReauthenticateWebAuthnForm, inputs.Input):
    pass


class AuthenticateWebAuthnInput(AuthenticateWebAuthnForm, inputs.Input):
    pass


class LoginWebAuthnInput(LoginWebAuthnForm, inputs.Input):
    pass


class SignupWebAuthnInput(BaseSignupForm, inputs.Input):
    pass


class TrustInput(inputs.Input):
    trust = inputs.BooleanField(required=False)
