from allauth.headless.internal.restkit import inputs
from allauth.mfa.base.forms import AuthenticateForm
from allauth.mfa.recovery_codes.forms import GenerateRecoveryCodesForm
from allauth.mfa.totp.forms import ActivateTOTPForm
from allauth.mfa.webauthn.forms import AddWebAuthnForm


class AuthenticateInput(AuthenticateForm, inputs.Input):
    pass


class ActivateTOTPInput(ActivateTOTPForm, inputs.Input):
    pass


class GenerateRecoveryCodesInput(GenerateRecoveryCodesForm, inputs.Input):
    pass


class AddWebAuthnInput(AddWebAuthnForm, inputs.Input):
    pass
