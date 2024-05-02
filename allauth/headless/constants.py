from enum import Enum

from allauth import app_settings as allauth_settings
from allauth.account.stages import EmailVerificationStage


class Client(str, Enum):
    APP = "app"
    BROWSER = "browser"


class Flow(str, Enum):
    VERIFY_EMAIL = EmailVerificationStage.key
    LOGIN = "login"
    LOGIN_BY_CODE = "login_by_code"
    SIGNUP = "signup"
    PROVIDER_REDIRECT = "provider_redirect"
    PROVIDER_SIGNUP = "provider_signup"
    PROVIDER_TOKEN = "provider_token"
    REAUTHENTICATE = "reauthenticate"
    MFA_REAUTHENTICATE = "mfa_reauthenticate"
    if allauth_settings.MFA_ENABLED:
        from allauth.mfa.stages import AuthenticateStage

        MFA_AUTHENTICATE = AuthenticateStage.key
