from __future__ import annotations

from django.http import HttpRequest, HttpResponse

from allauth.core.exceptions import RateLimited  # noqa
from allauth.core.internal import ratelimit as _impl
from allauth.core.internal.ratelimit import Rate  # noqa
from allauth.core.internal.ratelimit import respond_429


__all__ = ("clear", "consume", "respond_429", "consume_or_429")


def clear(request: HttpRequest, *, action: str, key=None, user=None) -> None:
    _impl.clear(
        request=request,
        app="allauth.account",
        action=action,
        key=key,
        user=user,
    )


def consume(
    request: HttpRequest,
    *,
    action,
    key=None,
    user=None,
    dry_run: bool = False,
    raise_exception: bool = False,
) -> bool:
    """
    TODO: We ened to deprecate this module and keep rate limiting internal
    to allauth. This method is using `allauth.account.app_settings` as a
    hard-coded source of settings, which is bad for reusability elsewhere.
    """
    usage = _impl.consume(
        request=request,
        app="allauth.account",
        action=action,
        key=key,
        user=user,
        dry_run=dry_run,
        raise_exception=raise_exception,
    )
    if not usage:
        return False
    return True


def consume_or_429(request: HttpRequest, *args, **kwargs) -> HttpResponse | None:
    return _impl.consume_or_429(request=request, app="allauth.account", **kwargs)
