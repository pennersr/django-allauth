import hashlib
import time
from collections import namedtuple

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render


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


def consume(request, *, action, key=None, user=None):
    from allauth.account import app_settings

    if not request or request.method == "GET":
        return True

    rates = _parse_rates(app_settings.RATE_LIMITS.get(action))
    if not rates:
        return True

    allowed = True
    for rate in rates:
        if not _consume_rate(request, action=action, rate=rate, key=key, user=user):
            allowed = False
    return allowed


def _consume_rate(request, *, action, rate, key=None, user=None):
    cache_key = _cache_key(request, action=action, rate=rate, key=key, user=user)
    history = cache.get(cache_key, [])
    now = time.time()
    while history and history[-1] <= now - rate.duration:
        history.pop()
    allowed = len(history) < rate.amount
    if allowed:
        history.insert(0, now)
        cache.set(cache_key, history, rate.duration)
    return allowed


def consume_or_429(request, *args, **kwargs):
    from allauth.account import app_settings

    if not consume(request, *args, **kwargs):
        return render(request, "429." + app_settings.TEMPLATE_EXTENSION, status=429)
