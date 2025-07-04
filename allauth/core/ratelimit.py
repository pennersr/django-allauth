from typing import Optional

from django.conf import settings
from django.http import HttpResponse

from allauth import app_settings
from allauth.core.exceptions import RateLimited  # noqa
from allauth.core.internal import ratelimit as _impl
from allauth.core.internal.ratelimit import Rate  # noqa
from allauth.utils import import_callable


def clear(request, *, action, key=None, user=None):
    from allauth.account import app_settings

    _impl.clear(
        request=request,
        config=app_settings.RATE_LIMITS,
        action=action,
        key=key,
        user=user,
    )


def consume(
    request,
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
    from allauth.account import app_settings

    usage = _impl.consume(
        request=request,
        config=app_settings.RATE_LIMITS,
        action=action,
        key=key,
        user=user,
        dry_run=dry_run,
        raise_exception=raise_exception,
    )
    if not usage:
        return False
    return True


def respond_429(request) -> HttpResponse:
    if app_settings.HEADLESS_ENABLED and hasattr(request.allauth, "headless"):
        from allauth.headless.base.response import RateLimitResponse

        return RateLimitResponse(request)

    try:
        handler429 = import_callable(settings.ROOT_URLCONF + ".handler429")
        handler429 = import_callable(handler429)
    except (ImportError, AttributeError):
        handler429 = _impl.handler429
    return handler429(request)


def consume_or_429(request, *args, **kwargs) -> Optional[HttpResponse]:
    if not consume(request, *args, **kwargs):
        return respond_429(request)
    return None
