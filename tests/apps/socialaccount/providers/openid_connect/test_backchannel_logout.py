from http import HTTPStatus
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.openid_connect._sessions import (
    BACKCHANNEL_LOGOUT_SESSION_KEY,
)
from allauth.socialaccount.providers.openid_connect.forms import (
    BACKCHANNEL_LOGOUT_EVENT,
)
from allauth.usersessions.models import UserSession
from tests.mocking import mocked_response


pytestmark = pytest.mark.django_db


@pytest.fixture
def logout_token_factory(app, oidc_info):
    def f(**kwargs):
        data = {
            "iss": oidc_info["issuer"],
            "aud": app.client_id,
            "iat": 123,
            "exp": 456,
            "jti": "jti-123",
            "events": {BACKCHANNEL_LOGOUT_EVENT: {}},
            "sid": "sid-123",
            "sub": "sub-123",
        }
        data.update(kwargs)
        return data

    return f


@pytest.fixture
def oidc_user(provider_id):
    user = get_user_model().objects.create_user(username="oidc-user")
    SocialAccount.objects.create(user=user, provider=provider_id, uid="sub-123")
    return user


@pytest.fixture
def client_with_backchannel_logout(client, app, oidc_user, provider_id):
    client.force_login(oidc_user)
    session = client.session
    session[BACKCHANNEL_LOGOUT_SESSION_KEY] = {
        provider_id: {"sid": "sid-123", "sub": "sub-123"}
    }
    session.save()
    UserSession.objects.create(
        user=oidc_user,
        session_key=session.session_key,
        ip="127.0.0.1",
        user_agent="",
    )
    return client


@pytest.fixture
def post_logout(client_with_backchannel_logout, oidc_info, provider_id):
    def post(token_data):
        url = reverse(
            "openid_connect_backchannel_logout",
            kwargs={"provider_id": provider_id},
        )
        with (
            mocked_response(oidc_info),
            patch(
                "allauth.socialaccount.providers.openid_connect.forms.jwtkit.verify_and_decode",
                return_value=token_data,
            ),
        ):
            data = {} if token_data is None else {"logout_token": "logout-token"}
            return client_with_backchannel_logout.post(url, data)

    return post


def test_logout_by_sid(post_logout, logout_token_factory, oidc_user):
    assert UserSession.objects.filter(user=oidc_user).exists()
    response = post_logout(logout_token_factory())

    assert response.status_code == HTTPStatus.OK
    assert "no-store" in response["Cache-Control"]
    assert not UserSession.objects.filter(user=oidc_user).exists()


@pytest.mark.parametrize(
    "token_overrides,error_description",
    [
        ({"events": None}, "The logout token contains invalid claims."),
        ({"sub": None}, "The logout token must contain `sub`."),
        (None, "The logout_token parameter is required."),
    ],
)
def test_rejects_invalid_logout(
    post_logout,
    logout_token_factory,
    oidc_user,
    token_overrides,
    error_description,
):
    token_data = (
        None if token_overrides is None else logout_token_factory(**token_overrides)
    )
    response = post_logout(token_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        "error": "invalid_request",
        "error_description": error_description,
    }
    assert UserSession.objects.filter(user=oidc_user).exists()
