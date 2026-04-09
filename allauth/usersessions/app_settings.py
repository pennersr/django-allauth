from __future__ import annotations

from typing import TypeVar


_T = TypeVar("_T")


class AppSettings:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def _setting(self, name: str, dflt: _T) -> _T:
        from allauth.utils import get_setting

        return get_setting(self.prefix + name, dflt)

    @property
    def ADAPTER(self) -> str:
        return self._setting(
            "ADAPTER", "allauth.usersessions.adapter.DefaultUserSessionsAdapter"
        )

    @property
    def TRACK_ACTIVITY(self) -> bool:
        """Whether or not sessions are to be actively tracked. When tracking is
        enabled, the last seen IP address and last seen timestamp will be kept
        track of.
        """
        return self._setting("TRACK_ACTIVITY", False)


_app_settings = AppSettings("USERSESSIONS_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
