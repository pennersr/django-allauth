from allauth.headless.restkit import inputs
from allauth.mfa.forms import (
    ActivateTOTPForm,
    AuthenticateForm,
    GenerateRecoveryCodesForm,
)


class AuthenticateInput(AuthenticateForm, inputs.Input):
    pass


class ActivateTOTPInput(ActivateTOTPForm, inputs.Input):
    pass


class GenerateRecoveryCodesInput(GenerateRecoveryCodesForm, inputs.Input):
    pass
