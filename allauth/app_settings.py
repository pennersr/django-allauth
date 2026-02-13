from typing import Optional

from django.apps import apps


class AppSettings:
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
    def SOCIALACCOUNT_ONLY(self) -> bool:
        from allauth.utils import get_setting

        return get_setting("SOCIALACCOUNT_ONLY", False)

    @property
    def MFA_ENABLED(self):
        return apps.is_installed("allauth.mfa")

    @property
    def USERSESSIONS_ENABLED(self):
        return apps.is_installed("allauth.usersessions")

    @property
    def HEADLESS_ENABLED(self):
        return apps.is_installed("allauth.headless")

    @property
    def HEADLESS_ONLY(self) -> bool:
        from allauth.utils import get_setting

        return get_setting("HEADLESS_ONLY", False)

    @property
    def DEFAULT_AUTO_FIELD(self):
        return self._setting("DEFAULT_AUTO_FIELD", None)

    @property
    def TRUSTED_PROXY_COUNT(self) -> int:
        """
        As the ``X-Forwarded-For`` header can be spoofed, you need to
        configure the number of proxies that are under your control and hence,
        can be trusted. The default is 0, meaning, no proxies are trusted.  As a
        result, the ``X-Forwarded-For`` header will be disregarded by default.
        """
        return self._setting("TRUSTED_PROXY_COUNT", 0)

    @property
    def TRUSTED_CLIENT_IP_HEADER(self) -> Optional[str]:
        """
        If your service is running behind a trusted proxy that sets a custom header
        containing the client IP address, specify that header name here. The client
        IP will be extracted from this header instead of ``X-Forwarded-For``.
        Examples: ``"CF-Connecting-IP"`` (Cloudflare), ``"X-Real-IP"`` (nginx).
        """
        return self._setting("TRUSTED_CLIENT_IP_HEADER", None)


_app_settings = AppSettings("ALLAUTH_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
