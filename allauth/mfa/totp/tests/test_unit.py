from unittest import mock

from allauth.mfa import app_settings
from allauth.mfa.totp.internal.auth import (
    format_hotp_value,
    generate_totp_secret,
    hotp_value,
    validate_totp_code,
    yield_hotp_counters_from_time,
)


@mock.patch("time.time", mock.MagicMock(return_value=1731948631))
def test_totp_counters_from_time():
    app_settings.TOTP_TOLERANCE = 0
    counters = list(yield_hotp_counters_from_time())
    assert len(counters) == 1


@mock.patch("time.time", mock.MagicMock(return_value=1731948631))
def test_totp_counters_from_time_with_tolerance():
    app_settings.TOTP_TOLERANCE = 1
    counters = list(yield_hotp_counters_from_time())
    assert len(counters) == 3


@mock.patch("time.time", mock.MagicMock(return_value=1731948631))
def test_validate_with_tolerance():
    app_settings.TOTP_TOLERANCE = 1
    test_secret = generate_totp_secret()
    expected_value = format_hotp_value(hotp_value(test_secret, 57731621))
    assert validate_totp_code(test_secret, expected_value)

    before_value = format_hotp_value(hotp_value(test_secret, 57731620))
    assert validate_totp_code(test_secret, before_value)

    after_value = format_hotp_value(hotp_value(test_secret, 57731622))
    assert validate_totp_code(test_secret, after_value)

    two_before_value = format_hotp_value(hotp_value(test_secret, 57731619))
    assert not validate_totp_code(test_secret, two_before_value)

    two_after_value = format_hotp_value(hotp_value(test_secret, 57731623))
    assert not validate_totp_code(test_secret, two_after_value)
