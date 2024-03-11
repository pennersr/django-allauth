from allauth.headless.restkit import inputs
from allauth.socialaccount.forms import SignupForm


class SignupInput(SignupForm, inputs.Input):
    pass
