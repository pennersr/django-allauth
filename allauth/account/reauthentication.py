import warnings

from allauth.account.internal.flows.reauthentication import (
    did_recently_authenticate,
    raise_if_reauthentication_required,
    reauthenticate_then_callback,
)


__all__ = [
    "reauthenticate_then_callback",
    "raise_if_reauthentication_required",
    "did_recently_authenticate",
]

warnings.warn("allauth.account.reauthentication is deprecated")
