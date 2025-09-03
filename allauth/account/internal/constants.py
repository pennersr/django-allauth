from enum import Enum


class LoginStageKey(str, Enum):
    LOGIN_BY_CODE = "login_by_code"
    VERIFY_EMAIL = "verify_email"
    VERIFY_PHONE = "verify_phone"
