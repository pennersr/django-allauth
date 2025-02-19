from enum import Enum

from allauth.account.stages import EmailVerificationStage, LoginByCodeStage


class Client(str, Enum):
    APP = "app"
    BROWSER = "browser"


class Flow(str, Enum):
    VERIFY_EMAIL = EmailVerificationStage.key
    LOGIN = "login"
    LOGIN_BY_CODE = LoginByCodeStage.key
    SIGNUP = "signup"
    PASSWORD_RESET_BY_CODE = "password_reset_by_code"  # nosec
    PROVIDER_REDIRECT = "provider_redirect"
    PROVIDER_SIGNUP = "provider_signup"
    PROVIDER_TOKEN = "provider_token"  # nosec
    REAUTHENTICATE = "reauthenticate"
    MFA_REAUTHENTICATE = "mfa_reauthenticate"
    MFA_AUTHENTICATE = "mfa_authenticate"  # NOTE: Equal to `allauth.mfa.stages.AuthenticationStage.key`
    MFA_LOGIN_WEBAUTHN = "mfa_login_webauthn"
    MFA_SIGNUP_WEBAUTHN = "mfa_signup_webauthn"
