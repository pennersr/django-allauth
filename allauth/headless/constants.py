from enum import Enum

from allauth.account.stages import EmailVerificationStage
from allauth.mfa.stages import AuthenticateStage


class Client(str, Enum):
    APP = "app"
    BROWSER = "browser"


class Flow(str, Enum):
    VERIFY_EMAIL = EmailVerificationStage.key
    LOGIN = "login"
    SIGNUP = "signup"
    PROVIDER_REDIRECT = "provider_redirect"
    PROVIDER_SIGNUP = "provider_signup"
    PROVIDER_TOKEN = "provider_token"
    MFA_AUTHENTICATE = AuthenticateStage.key
    REAUTHENTICATE = "reauthenticate"
    MFA_REAUTHENTICATE = "mfa_reauthenticate"
