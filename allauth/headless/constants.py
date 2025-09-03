from enum import Enum

from allauth.account.internal.constants import LoginStageKey as AccountLoginStageKey
from allauth.mfa.internal.constants import LoginStageKey as MFALoginStageKey


class Client(str, Enum):
    APP = "app"
    BROWSER = "browser"


class Flow(str, Enum):
    LOGIN = "login"
    LOGIN_BY_CODE = AccountLoginStageKey.LOGIN_BY_CODE.value
    MFA_AUTHENTICATE = MFALoginStageKey.MFA_AUTHENTICATE.value
    MFA_LOGIN_WEBAUTHN = "mfa_login_webauthn"
    MFA_REAUTHENTICATE = "mfa_reauthenticate"
    MFA_SIGNUP_WEBAUTHN = MFALoginStageKey.MFA_SIGNUP_WEBAUTHN.value
    MFA_TRUST = MFALoginStageKey.MFA_TRUST.value
    PASSWORD_RESET_BY_CODE = "password_reset_by_code"  # nosec
    PROVIDER_REDIRECT = "provider_redirect"
    PROVIDER_SIGNUP = "provider_signup"
    PROVIDER_TOKEN = "provider_token"  # nosec
    REAUTHENTICATE = "reauthenticate"
    SIGNUP = "signup"
    VERIFY_EMAIL = AccountLoginStageKey.VERIFY_EMAIL.value
    VERIFY_PHONE = AccountLoginStageKey.VERIFY_PHONE.value
