from django.apps import apps


class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def SITES_ENABLED(self):
        return apps.is_installed("django.contrib.sites")

    @property
    def SOCIALACCOUNT_ENABLED(self):
        return apps.is_installed("allauth.socialaccount")

    @property
    def MFA_ENABLED(self):
        return apps.is_installed("allauth.mfa")

    @property
    def USERSESSIONS_ENABLED(self):
        return apps.is_installed("allauth.usersessions")

    @property
    def DEFAULT_AUTO_FIELD(self):
        return self._setting("DEFAULT_AUTO_FIELD", None)


_app_settings = AppSettings("ALLAUTH_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
