import time
from contextlib import contextmanager
from unittest.mock import patch

from django.urls import reverse

import pytest

from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import statekit
from allauth.socialaccount.models import SocialAccount, SocialLogin, SocialToken
from allauth.socialaccount.providers.base.constants import AuthProcess
from tests.mocking import MockedResponse, mocked_response


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
        provider_instance = get_adapter().get_provider(request=None, provider=provider)
        account = SocialAccount(provider=provider, uid=uid)
        sociallogin = SocialLogin(
            provider=provider_instance, user=user, account=account
        )
        if with_email:
            sociallogin.email_addresses = [
                EmailAddress(email=user.email, verified=email_verified, primary=True)
            ]
        if with_token:
            sociallogin.token = SocialToken(token="123", token_secret="456")  # nosec
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


@pytest.fixture
def provider_callback_response():
    def f(client, process=AuthProcess.LOGIN):
        with mocked_response(
            {
                "token_endpoint": "/",
                "userinfo_endpoint": "/",
            },
            MockedResponse(200, "access_token=456", {"content-type": "dummy"}),
            {
                "sub": "sub123",
            },
        ):
            session = client.session
            session[statekit.STATES_SESSION_KEY] = {
                "state456": [{"process": process}, time.time()]
            }
            session.save()

            resp = client.post(
                reverse(
                    "openid_connect_callback",
                    kwargs={"provider_id": "unittest-server"},
                )
                + "?code=123&state=state456"
            )
            return resp

    return f
