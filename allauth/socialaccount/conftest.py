from contextlib import contextmanager
from unittest.mock import patch

import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import (
    SocialAccount,
    SocialLogin,
    SocialToken,
)


@pytest.fixture
def sociallogin_factory(user_factory):
    def factory(
        email=None,
        username=None,
        with_email=True,
        provider="unittest-server",
        uid="123",
        email_verified=True,
        with_token=False,
    ):
        user = user_factory(
            username=username, email=email, commit=False, with_email=with_email
        )
        account = SocialAccount(provider=provider, uid=uid)
        sociallogin = SocialLogin(user=user, account=account)
        if with_email:
            sociallogin.email_addresses = [
                EmailAddress(email=user.email, verified=email_verified, primary=True)
            ]
        if with_token:
            sociallogin.token = SocialToken(token="123", token_secret="456")
        return sociallogin

    return factory


@pytest.fixture
def jwt_decode_bypass():
    @contextmanager
    def f(jwt_data):
        with patch("allauth.socialaccount.internal.jwtkit.verify_and_decode") as m:
            data = {
                "iss": "https://accounts.google.com",
                "aud": "client_id",
                "sub": "123sub",
                "hd": "example.com",
                "email": "raymond@example.com",
                "email_verified": True,
                "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
                "name": "Raymond Penners",
                "picture": "https://lh5.googleusercontent.com/photo.jpg",
                "given_name": "Raymond",
                "family_name": "Penners",
                "locale": "en",
                "iat": 123,
                "exp": 456,
            }
            data.update(jwt_data)
            m.return_value = data
            yield

    return f
