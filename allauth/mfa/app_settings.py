class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def ADAPTER(self):
        return self._setting("ADAPTER", "allauth.mfa.adapter.DefaultMFAAdapter")

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
    def SUPPORTED_TYPES(self):
        dflt = ["recovery_codes", "totp"]
        return self._setting("SUPPORTED_TYPES", dflt)


_app_settings = AppSettings("MFA_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
