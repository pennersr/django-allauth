from enum import Enum


class LoginStageKey(str, Enum):
    MFA_SIGNUP_WEBAUTHN = "mfa_signup_webauthn"
    MFA_AUTHENTICATE = "mfa_authenticate"
    MFA_TRUST = "mfa_trust"
