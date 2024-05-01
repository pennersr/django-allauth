import pytest

from allauth.mfa import recovery_codes, totp


@pytest.fixture
def user_with_totp(user):
    totp.TOTP.activate(user, totp.generate_totp_secret())
    return user


@pytest.fixture
def user_with_recovery_codes(user_with_totp):
    recovery_codes.RecoveryCodes.activate(user_with_totp)
    return user_with_totp
