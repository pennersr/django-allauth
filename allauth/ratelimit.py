import time
from collections import namedtuple

from django.core.cache import cache
from django.shortcuts import render


Rate = namedtuple("Rate", "amount duration")


def parse(rate):
    ret = None
    if rate:
        amount, duration = rate.split("/")
        amount = int(amount)
        duration_map = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if duration not in duration_map:
            raise ValueError("Invalid duration: %s" % duration)
        duration = duration_map[duration]
        ret = Rate(amount, duration)
    return ret


def consume(request, *, action, key=None, amount=None, duration=None, user=None):
    allowed = True
    from allauth.account import app_settings
    from allauth.account.adapter import get_adapter

    rate = app_settings.RATE_LIMITS.get(action)
    if rate:
        rate = parse(rate)
        if not amount:
            amount = rate.amount
        if not duration:
            duration = rate.duration

    if request.method == "GET" or not amount or not duration:
        pass
    else:
        if user or request.user.is_authenticated:
            source = ("user", str((user or request.user).pk))
        else:
            source = ("ip", get_adapter().get_client_ip(request))
        keys = ["allauth", "rl", action, *source]
        if key is not None:
            keys.append(key)
        cache_key = ":".join(keys)
        history = cache.get(cache_key, [])
        now = time.time()
        while history and history[-1] <= now - duration:
            history.pop()
        allowed = len(history) < amount
        if allowed:
            history.insert(0, now)
            cache.set(cache_key, history, duration)
    return allowed


def consume_or_429(request, *args, **kwargs):
    from allauth.account import app_settings

    if not consume(request, *args, **kwargs):
        return render(request, "429." + app_settings.TEMPLATE_EXTENSION, status=429)
