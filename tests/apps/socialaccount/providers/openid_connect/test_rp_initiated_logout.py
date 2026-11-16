from urllib.parse import parse_qs, urlparse

from django.contrib.auth import SESSION_KEY, get_user_model
from django.urls import reverse

import pytest

from allauth.socialaccount.providers.openid_connect._sessions import (
    BACKCHANNEL_LOGOUT_SESSION_KEY,
)
from tests.mocking import mocked_response


pytestmark = pytest.mark.django_db


@pytest.fixture
def oidc_client(client, app, provider_id):
    user = get_user_model().objects.create_user(username="oidc-user")
    client.force_login(user)
    session = client.session
    session[BACKCHANNEL_LOGOUT_SESSION_KEY] = {
        provider_id: {
            "id_token": "id-token",
            "sid": "sid-123",
            "sub": "sub-123",
        }
    }
    session.save()
    return client


def logout_url(provider_id):
    return reverse("openid_connect_logout", kwargs={"provider_id": provider_id})


def logout_callback_url(provider_id):
    return reverse(
        "openid_connect_logout_callback", kwargs={"provider_id": provider_id}
    )


def test_logout(oidc_client, app, oidc_info, provider_id):
    with mocked_response(oidc_info):
        response = oidc_client.post(
            logout_url(provider_id),
            data={"next": "/after-logout/"},
        )

    parsed = urlparse(response.url)
    query = parse_qs(parsed.query)
    assert parsed.scheme == "https"
    assert parsed.netloc == "issuer.example.com"
    assert parsed.path == "/logout"
    assert query == {
        "client_id": [app.client_id],
        "id_token_hint": ["id-token"],
        "post_logout_redirect_uri": [
            "http://testserver/accounts/oidc/oidc-server/logout/callback/"
        ],
        "state": query["state"],
    }
    assert SESSION_KEY not in oidc_client.session

    response = oidc_client.get(
        logout_callback_url(provider_id),
        data={"state": query["state"][0]},
    )
    assert response.url == "/after-logout/"


def test_logout_without_id_token(oidc_client, app, oidc_info, provider_id):
    session = oidc_client.session
    sessions = session[BACKCHANNEL_LOGOUT_SESSION_KEY]
    sessions[provider_id].pop("id_token")
    session[BACKCHANNEL_LOGOUT_SESSION_KEY] = sessions
    session.save()

    with mocked_response(oidc_info):
        response = oidc_client.post(logout_url(provider_id))

    query = parse_qs(urlparse(response.url).query)
    assert "id_token_hint" not in query
    assert query["client_id"] == [app.client_id]


def test_logout_not_supported(oidc_client, oidc_info, provider_id):
    oidc_info.pop("end_session_endpoint")
    with mocked_response(oidc_info):
        response = oidc_client.post(
            logout_url(provider_id),
            data={"next": "/after-logout/"},
        )

    assert response.url == "/after-logout/"
    assert SESSION_KEY not in oidc_client.session


def test_logout_requires_post(client, provider_id):
    response = client.get(logout_url(provider_id))
    assert response.status_code == 405


def test_logout_callback_invalid_state(client, settings, provider_id):
    settings.ACCOUNT_LOGOUT_REDIRECT_URL = "/logged-out/"
    response = client.get(
        logout_callback_url(provider_id),
        data={"state": "invalid"},
    )
    assert response.url == "/logged-out/"


def test_logout_rejects_unsafe_next(oidc_client, oidc_info, provider_id, settings):
    settings.ACCOUNT_LOGOUT_REDIRECT_URL = "/safe/"
    with mocked_response(oidc_info):
        response = oidc_client.post(
            logout_url(provider_id),
            data={"next": "https://evil.example/"},
        )
    state = parse_qs(urlparse(response.url).query)["state"][0]
    response = oidc_client.get(
        logout_callback_url(provider_id),
        data={"state": state},
    )
    assert response.url == "/safe/"
