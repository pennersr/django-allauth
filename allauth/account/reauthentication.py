import warnings

from allauth.account.internal.flows.reauthentication import (
    did_recently_authenticate,
    raise_if_reauthentication_required,
)


__all__ = [
    "raise_if_reauthentication_required",
    "did_recently_authenticate",
]

warnings.warn("allauth.account.reauthentication is deprecated")
