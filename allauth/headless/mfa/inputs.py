from allauth.headless.restkit import inputs
from allauth.mfa.forms import ActivateTOTPForm, AuthenticateForm


class AuthenticateInput(AuthenticateForm, inputs.Input):
    pass


class ActivateTOTPInput(ActivateTOTPForm, inputs.Input):
    pass
