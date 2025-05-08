import hashlib
import time
from collections import namedtuple
from typing import Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import render

from allauth import app_settings
from allauth.core.exceptions import RateLimited
from allauth.utils import import_callable


Rate = namedtuple("Rate", "amount duration per")


def _parse_duration(duration):
    if len(duration) == 0:
        raise ValueError(duration)
    unit = duration[-1]
    value = duration[0:-1]
    unit_map = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if unit not in unit_map:
        raise ValueError("Invalid duration unit: %s" % unit)
    if len(value) == 0:
        value = 1
    else:
        value = float(value)
    return value * unit_map[unit]


def _parse_rate(rate):
    parts = rate.split("/")
    if len(parts) == 2:
        amount, duration = parts
        per = "ip"
    elif len(parts) == 3:
        amount, duration, per = parts
    else:
        raise ValueError(rate)
    amount = int(amount)
    duration = _parse_duration(duration)
    return Rate(amount, duration, per)


def _parse_rates(rates):
    ret = []
    if rates:
        rates = rates.strip()
        if rates:
            parts = rates.split(",")
            for part in parts:
                ret.append(_parse_rate(part.strip()))
    return ret


def _cache_key(request, *, action, rate, key=None, user=None):
    from allauth.account.adapter import get_adapter

    if rate.per == "ip":
        source = ("ip", get_adapter().get_client_ip(request))
    elif rate.per == "user":
        if user is None:
            if not request.user.is_authenticated:
                raise ImproperlyConfigured(
                    "ratelimit configured per user but used anonymously"
                )
            user = request.user
        source = ("user", str(user.pk))
    elif rate.per == "key":
        if key is None:
            raise ImproperlyConfigured(
                "ratelimit configured per key but no key specified"
            )
        key_hash = hashlib.sha256(key.encode("utf8")).hexdigest()
        source = (key_hash,)
    else:
        raise ValueError(rate.per)
    keys = ["allauth", "rl", action, *source]
    return ":".join(keys)


def clear(request, *, action, key=None, user=None):
    from allauth.account import app_settings

    rates = _parse_rates(app_settings.RATE_LIMITS.get(action))
    for rate in rates:
        cache_key = _cache_key(request, action=action, rate=rate, key=key, user=user)
        cache.delete(cache_key)


def consume(
    request,
    *,
    action,
    key=None,
    user=None,
    dry_run: bool = False,
    raise_exception: bool = False
) -> bool:
    from allauth.account import app_settings

    if not request or request.method == "GET":
        return True

    rates = _parse_rates(app_settings.RATE_LIMITS.get(action))
    if not rates:
        return True

    allowed = True
    for rate in rates:
        if not _consume_rate(
            request,
            action=action,
            rate=rate,
            key=key,
            user=user,
            dry_run=dry_run,
            raise_exception=raise_exception,
        ):
            allowed = False
    return allowed


def _consume_rate(
    request,
    *,
    action,
    rate,
    key=None,
    user=None,
    dry_run: bool = False,
    raise_exception: bool = False
):
    cache_key = _cache_key(request, action=action, rate=rate, key=key, user=user)
    history = cache.get(cache_key, [])
    now = time.time()
    while history and history[-1] <= now - rate.duration:
        history.pop()
    allowed = len(history) < rate.amount
    if allowed and not dry_run:
        history.insert(0, now)
        cache.set(cache_key, history, rate.duration)
    if not allowed and raise_exception:
        raise RateLimited
    return allowed


def _handler429(request):
    from allauth.account import app_settings

    return render(request, "429." + app_settings.TEMPLATE_EXTENSION, status=429)


def respond_429(request) -> HttpResponse:
    if app_settings.HEADLESS_ENABLED and hasattr(request.allauth, "headless"):
        from allauth.headless.base.response import RateLimitResponse

        return RateLimitResponse(request)

    try:
        handler429 = import_callable(settings.ROOT_URLCONF + ".handler429")
        handler429 = import_callable(handler429)
    except (ImportError, AttributeError):
        handler429 = _handler429
    return handler429(request)


def consume_or_429(request, *args, **kwargs) -> Optional[HttpResponse]:
    if not consume(request, *args, **kwargs):
        return respond_429(request)
    return None
