from datetime import timedelta
from typing import Optional


class AppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def ADAPTER(self):
        return self._setting("ADAPTER", "allauth.mfa.adapter.DefaultMFAAdapter")

    @property
    def ALLOW_UNVERIFIED_EMAIL(self) -> bool:
        return self._setting("ALLOW_UNVERIFIED_EMAIL", False)

    @property
    def FORMS(self):
        return self._setting("FORMS", {})

    @property
    def RECOVERY_CODE_COUNT(self):
        """
        The number of recovery codes.
        """
        return self._setting("RECOVERY_CODE_COUNT", 10)

    @property
    def RECOVERY_CODE_DIGITS(self):
        """
        The number of digits of each recovery code.
        """
        return self._setting("RECOVERY_CODE_DIGITS", 8)

    @property
    def TOTP_PERIOD(self):
        """
        The period that a TOTP code will be valid for, in seconds.
        """
        return self._setting("TOTP_PERIOD", 30)

    @property
    def TOTP_DIGITS(self):
        """
        The number of digits for TOTP codes
        """
        return self._setting("TOTP_DIGITS", 6)

    @property
    def TOTP_ISSUER(self):
        """
        The issuer.
        """
        return self._setting("TOTP_ISSUER", "")

    @property
    def TOTP_INSECURE_BYPASS_CODE(self):
        """
        Don't use this on production. Useful for development & E2E tests only.
        """
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured

        code = self._setting("TOTP_INSECURE_BYPASS_CODE", None)
        if (not settings.DEBUG) and code:
            raise ImproperlyConfigured(
                "MFA_TOTP_INSECURE_BYPASS_CODE is for testing purposes only"
            )
        return code

    @property
    def TOTP_TOLERANCE(self):
        """
        The number of time steps in the past or future to allow. Lower values are more secure, but more likely to fail due to clock drift.
        """
        return self._setting("TOTP_TOLERANCE", 0)

    @property
    def SUPPORTED_TYPES(self):
        dflt = ["recovery_codes", "totp"]
        return self._setting("SUPPORTED_TYPES", dflt)

    @property
    def WEBAUTHN_ALLOW_INSECURE_ORIGIN(self):
        return self._setting("WEBAUTHN_ALLOW_INSECURE_ORIGIN", False)

    @property
    def PASSKEY_LOGIN_ENABLED(self) -> bool:
        return "webauthn" in self.SUPPORTED_TYPES and self._setting(
            "PASSKEY_LOGIN_ENABLED", False
        )

    @property
    def PASSKEY_SIGNUP_ENABLED(self) -> bool:
        return "webauthn" in self.SUPPORTED_TYPES and self._setting(
            "PASSKEY_SIGNUP_ENABLED", False
        )

    @property
    def TRUST_ENABLED(self) -> bool:
        return self._setting("TRUST_ENABLED", False)

    @property
    def TRUST_COOKIE_AGE(self) -> timedelta:
        age = self._setting("TRUST_COOKIE_AGE", timedelta(days=14))
        if not isinstance(age, timedelta):
            age = timedelta(seconds=age)
        return age

    @property
    def TRUST_COOKIE_NAME(self) -> str:
        return self._setting("TRUST_COOKIE_NAME", "mfa_trusted")

    @property
    def TRUST_COOKIE_DOMAIN(self) -> Optional[str]:
        from django.conf import settings

        return self._setting("TRUST_COOKIE_DOMAIN", settings.SESSION_COOKIE_DOMAIN)

    @property
    def TRUST_COOKIE_HTTPONLY(self) -> bool:
        from django.conf import settings

        return self._setting("TRUST_COOKIE_HTTPONLY", settings.SESSION_COOKIE_HTTPONLY)

    @property
    def TRUST_COOKIE_PATH(self) -> str:
        from django.conf import settings

        return self._setting("TRUST_COOKIE_PATH", settings.SESSION_COOKIE_PATH)

    @property
    def TRUST_COOKIE_SAMESITE(self) -> str:
        from django.conf import settings

        return self._setting("TRUST_COOKIE_SAMESITE", settings.SESSION_COOKIE_SAMESITE)

    @property
    def TRUST_COOKIE_SECURE(self) -> Optional[str]:
        from django.conf import settings

        return self._setting("TRUST_COOKIE_SECURE", settings.SESSION_COOKIE_SECURE)


_app_settings = AppSettings("MFA_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
