"""
See the "Deployment Requirements" over at ``docs/common/rate_limits.rst``
for certain trade-offs made in this implementation.
"""

from __future__ import annotations

import hashlib
import ipaddress
import time
from collections import namedtuple
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.utils.module_loading import import_string

from allauth import app_settings
from allauth.core.exceptions import RateLimited
from allauth.utils import import_callable


Rate = namedtuple("Rate", "amount duration per")

CACHE_LOCK_TIMEOUT = 10
CACHE_LOCK_WAIT_TIMEOUT = 1
CACHE_LOCK_RETRY_INTERVAL = 0.01
CACHE_LOCK_MAX_RETRY_INTERVAL = 0.1


@contextmanager
def cache_lock(cache_key: str) -> Iterator[bool]:
    lock_key = f"{cache_key}:lock"
    deadline = time.monotonic() + CACHE_LOCK_WAIT_TIMEOUT
    retry_interval = CACHE_LOCK_RETRY_INTERVAL
    while not cache.add(lock_key, True, timeout=CACHE_LOCK_TIMEOUT):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            yield False
            return
        time.sleep(min(retry_interval, remaining))
        retry_interval = min(retry_interval * 2, CACHE_LOCK_MAX_RETRY_INTERVAL)
    try:
        yield True
    finally:
        # Note that there is no guarantee that the following statement actually
        # deletes the lock that was acquired by this process. Given that the
        # critical section performs very few actions, and, given a sufficiently
        # large `CACHE_LOCK_TIMEOUT`, that should normally not happen.
        cache.delete(lock_key)


@dataclass
class SingleRateLimitUsage:
    cache_key: str
    cache_duration: float | int
    timestamp: float

    def rollback(self) -> None:
        with cache_lock(self.cache_key) as locked:
            if locked:
                history = cache.get(self.cache_key, [])
                history = [ts for ts in history if ts != self.timestamp]
                cache.set(self.cache_key, history, self.cache_duration)
            else:
                # Unable to rollback. That is nothing to worry about, skipping
                # only makes the limit more restrictive.
                pass


@dataclass
class RateLimitUsage:
    usage: list[SingleRateLimitUsage]

    def rollback(self) -> None:
        for usage in self.usage:
            usage.rollback()


def parse_duration(duration) -> int | float:
    if len(duration) == 0:
        raise ValueError(duration)
    unit = duration[-1]
    value = duration[0:-1]
    unit_map = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if unit not in unit_map:
        raise ValueError(f"Invalid duration unit: {unit}")
    if len(value) == 0:
        value = 1
    else:
        value = float(value)
    return value * unit_map[unit]


def parse_rate(rate: str) -> Rate:
    parts = rate.split("/")
    if len(parts) == 2:
        amount, duration = parts
        per = "ip"
    elif len(parts) == 3:
        amount, duration, per = parts
    else:
        raise ValueError(rate)
    amount_v = int(amount)
    duration_v = parse_duration(duration)
    return Rate(amount_v, duration_v, per)


def parse_rates(rates: str | None) -> list[Rate]:
    ret = []
    if rates:
        rates = rates.strip()
        if rates:
            parts = rates.split(",")
            for part in parts:
                ret.append(parse_rate(part.strip()))
    return ret


def truncate_ip(ip: str) -> str:
    from allauth import app_settings as allauth_settings

    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip

    if isinstance(addr, ipaddress.IPv6Address):
        prefix = allauth_settings.RATE_LIMIT_IPV6_PREFIX
        network = ipaddress.IPv6Network(f"{addr}/{prefix}", strict=False)
        return str(network.network_address)
    return ip


def get_ip(request: HttpRequest) -> str:
    from allauth.account.adapter import get_adapter

    ip = get_adapter().get_client_ip(request)
    return truncate_ip(ip)


def get_cache_key(
    request: HttpRequest, *, app: str, action: str, rate: Rate, key=None, user=None
) -> str:
    source: tuple[str, ...]
    if rate.per == "ip":
        source = ("ip", get_ip(request))
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
    keys = ["allauth", "rl", app, action, *source]
    return ":".join(keys)


def apply_rate(
    history: list[float], now: float, rate: Rate, *, dry_run: bool = False
) -> tuple[bool, list[float]]:
    """Apply ``rate`` to the hit timestamps at ``now``, returning
    ``(allowed, history)``: expired timestamps are dropped and, unless
    ``dry_run``, an allowed hit is recorded. I/O-free, so needs no cache.
    """
    while history and history[-1] <= now - rate.duration:
        history.pop()
    allowed = len(history) < rate.amount
    if allowed and not dry_run:
        history.insert(0, now)
    return allowed, history


def _consume_single_rate(
    request: HttpRequest,
    *,
    app: str,
    action: str,
    rate: Rate,
    key=None,
    user=None,
    dry_run: bool = False,
    raise_exception: bool = False,
) -> SingleRateLimitUsage | None:
    cache_key = get_cache_key(
        request, app=app, action=action, rate=rate, key=key, user=user
    )
    with cache_lock(cache_key) as locked:
        if not locked:
            if raise_exception:
                raise RateLimited
            return None
        history = cache.get(cache_key, [])
        now = time.time()
        allowed, history = apply_rate(history, now, rate, dry_run=dry_run)
        if allowed:
            usage = SingleRateLimitUsage(
                cache_key=cache_key, timestamp=now, cache_duration=rate.duration
            )
            if not dry_run:
                cache.set(cache_key, history, rate.duration)
        else:
            usage = None
            if raise_exception:
                raise RateLimited
        return usage


def get_rates(
    *, app: str, action: str, config: dict[str, str] | None = None
) -> list[Rate]:
    if config is None:
        config = import_string(f"{app}.app_settings.RATE_LIMITS")
    return parse_rates(config.get(action))


def consume(
    request: HttpRequest,
    *,
    app: str,
    action: str,
    config: dict[str, str] | None = None,
    key=None,
    user=None,
    dry_run: bool = False,
    limit_get: bool = False,
    raise_exception: bool = False,
) -> RateLimitUsage | None:
    usage = RateLimitUsage(usage=[])
    if (not limit_get) and request.method == "GET":
        return usage
    rates = get_rates(app=app, action=action, config=config)
    if not rates:
        return usage
    allowed = True
    for rate in rates:
        single_usage = _consume_single_rate(
            request,
            app=app,
            action=action,
            rate=rate,
            key=key,
            user=user,
            dry_run=dry_run,
            raise_exception=raise_exception,
        )
        if not single_usage:
            allowed = False
            break
        usage.usage.append(single_usage)
    return usage if allowed else None


def handler429(request: HttpRequest) -> HttpResponse:
    from allauth.account import app_settings

    try:
        return render(
            request,
            f"429.{app_settings.TEMPLATE_EXTENSION}",
            status=HTTPStatus.TOO_MANY_REQUESTS,
        )
    except TemplateDoesNotExist:
        content = """<html>
    <head><title>Too Many Requests</title></head>
    <body>
        <h1>429 Too Many Requests</h1>
        <p>You have sent too many requests. Please try again later.</p>
    </body>
</html>"""
        return HttpResponse(
            content=content,
            content_type="text/html",
            status=HTTPStatus.TOO_MANY_REQUESTS,
        )


def clear(
    request: HttpRequest,
    *,
    app: str,
    action: str,
    config: dict[str, str] | None = None,
    key=None,
    user=None,
) -> None:
    rates = get_rates(app=app, action=action, config=config)
    for rate in rates:
        cache_key = get_cache_key(
            request, app=app, action=action, rate=rate, key=key, user=user
        )
        with cache_lock(cache_key) as locked:
            if locked:
                cache.delete(cache_key)


def respond_429(request: HttpRequest) -> HttpResponse:
    if app_settings.HEADLESS_ENABLED and hasattr(
        request.allauth,  # type:ignore[attr-defined]
        "headless",
    ):
        from allauth.headless.base.response import RateLimitResponse

        return RateLimitResponse(request)

    try:
        h429 = import_callable(f"{settings.ROOT_URLCONF}.handler429")
        h429 = import_callable(h429)
    except (ImportError, AttributeError):
        h429 = handler429
    return h429(request)


def consume_or_429(request: HttpRequest, *args, **kwargs) -> HttpResponse | None:
    if not consume(request, *args, **kwargs):
        return respond_429(request)
    return None


def decorator(**rl_kwargs):
    def f(function):
        @wraps(function)
        def wrap(request: HttpRequest, *args, **kwargs):
            resp = consume_or_429(request, **rl_kwargs)
            if not resp:
                resp = function(request, *args, **kwargs)
            return resp

        return wrap

    return f
