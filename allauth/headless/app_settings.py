from typing import Optional, Tuple


class AppSettings:
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def ADAPTER(self):
        return self._setting(
            "ADAPTER", "allauth.headless.adapter.DefaultHeadlessAdapter"
        )

    @property
    def TOKEN_STRATEGY(self):
        from allauth.utils import import_attribute

        path = self._setting(
            "TOKEN_STRATEGY", "allauth.headless.tokens.sessions.SessionTokenStrategy"
        )
        cls = import_attribute(path)
        return cls()

    @property
    def SERVE_SPECIFICATION(self) -> bool:
        return self._setting("SERVE_SPECIFICATION", False)

    @property
    def SPECIFICATION_TEMPLATE_NAME(self) -> Optional[str]:
        return self._setting(
            "SPECIFICATION_TEMPLATE_NAME", "headless/spec/redoc_cdn.html"
        )

    @property
    def CLIENTS(self) -> Tuple[str]:
        return tuple(self._setting("CLIENTS", ("browser", "app")))

    @property
    def FRONTEND_URLS(self):
        return self._setting("FRONTEND_URLS", {})


_app_settings = AppSettings("HEADLESS_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
