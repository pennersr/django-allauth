from contextlib import contextmanager
from unittest.mock import patch

import pytest

from allauth.mfa import recovery_codes, totp


@pytest.fixture
def user_with_totp(user):
    totp.TOTP.activate(user, totp.generate_totp_secret())
    return user


@pytest.fixture
def user_with_recovery_codes(user):
    recovery_codes.RecoveryCodes.activate(user)
    return user


@pytest.fixture
def totp_validation_bypass():
    @contextmanager
    def f():
        with patch("allauth.mfa.totp.validate_totp_code") as m:
            m.return_value = True
            yield

    return f
