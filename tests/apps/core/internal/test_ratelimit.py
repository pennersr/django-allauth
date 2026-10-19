from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, BrokenBarrierError

from django.core.cache import caches
from django.http import HttpResponse

import pytest

from allauth.core.internal import ratelimit


def handler429(request):
    return HttpResponse("custom", status=429)


def test_respond_429_custom_handler(rf, settings):
    settings.ROOT_URLCONF = __name__
    request = rf.get("/")
    request.allauth = object()

    response = ratelimit.respond_429(request)

    assert response.status_code == 429
    assert response.content == b"custom"


def test_rollback_consume(rf, enable_cache):
    def consume():
        request = rf.post("/")
        config = {"foo": "2/m/ip"}
        return ratelimit.consume(request, config=config, app="app", action="foo")

    usage1 = consume()
    assert len(usage1.usage) > 0
    usage2 = consume()
    assert len(usage2.usage) > 0
    no_usage = consume()
    assert no_usage is None
    usage1.rollback()
    assert consume()
    assert not consume()


def test_concurrent_consume(rf, enable_cache, monkeypatch):
    request = rf.post("/")
    action = "foo"
    key = "subject"
    config = {action: "2/m/key"}
    rate = ratelimit.parse_rates(config[action])[0]
    cache_key = ratelimit.get_cache_key(
        request, app="app", action=action, rate=rate, key=key
    )

    cache_backend_class = type(caches["default"])
    original_get = cache_backend_class.get
    workers = 5
    read_barrier = Barrier(workers)

    def synchronized_get(self, key, *args, **kwargs):
        value = original_get(self, key, *args, **kwargs)
        if key == cache_key:
            try:
                # We have locking in place, so this should time out.
                read_barrier.wait(timeout=0.1)
                assert False, "concurrent access to rate-limit history"
            except BrokenBarrierError:
                pass
        return value

    monkeypatch.setattr(cache_backend_class, "get", synchronized_get)
    start_barrier = Barrier(workers)

    def consume(_):
        start_barrier.wait()
        return ratelimit.consume(
            request, app="app", action=action, config=config, key=key
        )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        usages = list(executor.map(consume, range(workers)))

    assert sum(usage is not None for usage in usages) == 2


def test_lock_contention_fails_closed(rf, enable_cache, monkeypatch):
    request = rf.post("/")
    config = {"foo": "2/m/key"}
    cache_backend_class = type(caches["default"])
    monkeypatch.setattr(ratelimit, "CACHE_LOCK_WAIT_TIMEOUT", 0)
    monkeypatch.setattr(cache_backend_class, "add", lambda *args, **kwargs: False)

    assert (
        ratelimit.consume(
            request, app="app", action="foo", config=config, key="subject"
        )
        is None
    )
    with pytest.raises(ratelimit.RateLimited):
        ratelimit.consume(
            request,
            app="app",
            action="foo",
            config=config,
            key="subject",
            raise_exception=True,
        )


def test_apply_rate():
    rate = ratelimit.Rate(amount=2, duration=60, per="ip")
    now = 1000.0

    # First hit against an empty history: allowed and recorded.
    allowed, history = ratelimit.apply_rate([], now, rate)
    assert allowed
    assert history == [now]

    # Second hit within the window: allowed, recorded newest-first.
    allowed, history = ratelimit.apply_rate(history, now + 1, rate)
    assert allowed
    assert history == [now + 1, now]

    # Third hit within the window: over the limit, nothing recorded.
    allowed, history = ratelimit.apply_rate(history, now + 2, rate)
    assert not allowed
    assert history == [now + 1, now]

    # A dry run never records, even when allowed.
    allowed, history = ratelimit.apply_rate([], now, rate, dry_run=True)
    assert allowed
    assert history == []

    # Timestamps older than the duration are dropped, freeing capacity.
    allowed, history = ratelimit.apply_rate([now - 61, now - 62], now, rate)
    assert allowed
    assert history == [now]


@pytest.mark.parametrize(
    "rate,values",
    [
        ("5/m", [(5, 60, "ip")]),
        ("5/m/user", [(5, 60, "user")]),
        ("2/3.5m/key", [(2, 210, "key")]),
        ("3/5m/user,20/0.5m/ip", [(3, 300, "user"), (20, 30, "ip")]),
        ("7/2h", [(7, 7200, "ip")]),
        ("7/0.25d", [(7, 21600, "ip")]),
    ],
)
def test_parse(rate, values):
    rates = ratelimit.parse_rates(rate)
    assert len(rates) == len(values)
    for i, rate in enumerate(rates):
        assert rate.amount == values[i][0]
        assert rate.duration == values[i][1]
        assert rate.per == values[i][2]


@pytest.mark.parametrize(
    "ip,prefix,expected",
    [
        ("192.168.1.1", 64, "192.168.1.1"),
        ("10.0.0.255", 48, "10.0.0.255"),
        ("2001:db8:85a3::8a2e:370:7334", 64, "2001:db8:85a3::"),
        ("2001:db8:85a3:1234:5678:abcd:ef01:2345", 64, "2001:db8:85a3:1234::"),
        ("2001:db8:85a3:1234:5678:abcd:ef01:2345", 48, "2001:db8:85a3::"),
        (
            "2001:db8:85a3:1234:5678:abcd:ef01:2345",
            128,
            "2001:db8:85a3:1234:5678:abcd:ef01:2345",
        ),
        ("::1", 64, "::"),
        ("invalid", 64, "invalid"),
    ],
)
def test_truncate_ip(ip, prefix, expected, settings):
    settings.ALLAUTH_RATE_LIMIT_IPV6_PREFIX = prefix
    assert ratelimit.truncate_ip(ip) == expected
