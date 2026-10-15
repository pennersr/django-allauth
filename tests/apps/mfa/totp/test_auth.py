from unittest.mock import patch

import pytest

from allauth.mfa import app_settings as mfa_app_settings
from allauth.mfa.models import Authenticator


@pytest.mark.parametrize("cache_add_result", [False, True])
def test_totp_code_is_claimed_atomically(user_with_totp, cache_add_result):
    totp = Authenticator.objects.get(
        user=user_with_totp, type=Authenticator.Type.TOTP
    ).wrap()
    with (
        patch("allauth.mfa.totp.internal.auth.validate_totp_code", return_value=True),
        patch("allauth.mfa.totp.internal.auth.cache.get") as cache_get,
        patch(
            "allauth.mfa.totp.internal.auth.cache.add", return_value=cache_add_result
        ) as cache_add,
    ):
        assert totp.validate_code("123456") is cache_add_result

    cache_get.assert_not_called()
    cache_add.assert_called_once_with(
        totp._get_used_cache_key("123456"),
        "y",
        timeout=mfa_app_settings.TOTP_PERIOD,
    )


def test_validate_non_ascii_code(user_with_totp):
    totp = Authenticator.objects.get(
        user=user_with_totp, type=Authenticator.Type.TOTP
    ).wrap()
    assert not totp.validate_code("€#")
