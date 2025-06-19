import pytest

from allauth.core.internal import ratelimit


def test_rollback_consume(rf, enable_cache):
    def consume():
        request = rf.post("/")
        config = {"foo": "2/m/ip"}
        return ratelimit.consume(request, config=config, action="foo")

    usage1 = consume()
    assert len(usage1.usage) > 0
    usage2 = consume()
    assert len(usage2.usage) > 0
    no_usage = consume()
    assert no_usage is None
    usage1.rollback()
    assert consume()
    assert not consume()


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
