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
            "TOKEN_STRATEGY",
            "allauth.headless.tokens.strategies.sessions.SessionTokenStrategy",
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

    @property
    def JWT_ALGORITHM(self) -> str:
        return self._setting("JWT_ALGORITHM", "RS256")

    @property
    def JWT_PRIVATE_KEY(self) -> str:
        return self._setting("JWT_PRIVATE_KEY", "")

    @property
    def JWT_ACCESS_TOKEN_EXPIRES_IN(self) -> int:
        return self._setting("JWT_ACCESS_TOKEN_EXPIRES_IN", 300)

    @property
    def JWT_REFRESH_TOKEN_EXPIRES_IN(self) -> int:
        return self._setting("JWT_REFRESH_TOKEN_EXPIRES_IN", 86400)

    @property
    def JWT_AUTHORIZATION_HEADER_SCHEME(self) -> str:
        return self._setting("JWT_AUTHORIZATION_HEADER_SCHEME", "Bearer")

    @property
    def JWT_STATEFUL_VALIDATION_ENABLED(self) -> bool:
        return self._setting("JWT_STATEFUL_VALIDATION_ENABLED", False)

    @property
    def JWT_ROTATE_REFRESH_TOKEN(self) -> bool:
        return self._setting("JWT_ROTATE_REFRESH_TOKEN", True)


_app_settings = AppSettings("HEADLESS_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
