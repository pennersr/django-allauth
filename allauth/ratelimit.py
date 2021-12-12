import time
from collections import namedtuple

from django.core.cache import cache


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


def consume(request, *, action, amount=None, duration=None):
    allowed = True
    from allauth.account.adapter import get_adapter

    if request.method == "GET" or not amount or not duration:
        pass
    else:
        if request.user.is_authenticated:
            source = ("user", str(request.user.pk))
        else:
            source = ("ip", get_adapter().get_client_ip(request))
        key = ":".join(["allauth", "rl", action, *source])
        history = cache.get(key, [])
        now = time.time()
        while history and history[-1] <= now - duration:
            history.pop()
        allowed = len(history) < amount
        if allowed:
            history.insert(0, now)
            cache.set(key, history, duration)
    return allowed
