import time
from contextlib import contextmanager

from django.core.cache import cache


class RateLimitExceeded(Exception):
    pass


@contextmanager
def rate_limit(request, action, amount, duration):
    from allauth.account.adapter import get_adapter

    if request.method != "GET" and duration > 0:
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
            yield
        else:
            raise RateLimitExceeded
    else:
        yield


def consume_rate_limit(*args, **kwargs):
    try:
        with rate_limit(*args, **kwargs):
            return True
    except RateLimitExceeded:
        return False
