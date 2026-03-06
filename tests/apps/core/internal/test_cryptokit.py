import pytest

from allauth.core.internal.cryptokit import compare_user_code, generate_user_code


@pytest.mark.parametrize(
    "actual,expected,result",
    [
        ("xkcd", "XKCD", True),
        ("XKCD", "xkcd", True),
        ("XK-CD", "XKCD", True),
        ("XK CD", "XKCD", True),
        ("XK - CD", "XKCD", True),
        ("XKCD", "XK-CD", True),
        ("ABCD", "XKCD", False),
        ("", "XKCD", False),
        ("XKCD", "", False),
        ("", "", False),
    ],
)
def test_compare_user_code(actual, expected, result):
    assert compare_user_code(actual=actual, expected=expected) is result


@pytest.mark.parametrize(
    "length,result",
    [
        (2, "X-X"),
        (3, "XX-X"),
        (6, "XXX-XXX"),
        (8, "XXXX-XXXX"),
        (9, "XXX-XXX-XXX"),
        (15, "XXXXX-XXXXX-XXXXX"),
    ],
)
def test_generate_user_code_dashing(length, result):
    assert generate_user_code(length=length, allowed_chars="X", dashed=True) == result
