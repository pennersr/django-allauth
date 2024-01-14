import pytest

from allauth.core import ratelimit


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
    rates = ratelimit._parse_rates(rate)
    assert len(rates) == len(values)
    for i, rate in enumerate(rates):
        assert rate.amount == values[i][0]
        assert rate.duration == values[i][1]
        assert rate.per == values[i][2]
