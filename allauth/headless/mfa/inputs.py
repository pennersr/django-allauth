from allauth.headless.restkit import inputs
from allauth.mfa.forms import AuthenticateForm


class AuthenticateInput(AuthenticateForm, inputs.Input):
    pass
