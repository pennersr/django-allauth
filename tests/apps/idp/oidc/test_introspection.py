import base64
import uuid
from datetime import timedelta
from http import HTTPStatus

from django.urls import reverse
from django.utils import timezone

import pytest
from oauthlib.common import Request

from allauth.core.context import request_context
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib.server import generate_jwt_access_token
from allauth.idp.oidc.models import Token


def _basic_auth(client_id: str, secret: str) -> str:
    raw = f"{client_id}:{secret}".encode()
    return "Basic " + base64.b64encode(raw).decode("ascii")


@pytest.fixture(autouse=True)
def introspection_enabled(settings_impacting_urls):
    with settings_impacting_urls(IDP_OIDC_INTROSPECTION_ENABLED=True):
        yield


@pytest.fixture
def jwt_access_token_factory(settings, rf):
    """Mint a *JWT*-formatted access token regardless of the parametrized format."""

    def f(client, user, scopes=["openid"]):
        settings.IDP_OIDC_ACCESS_TOKEN_FORMAT = "jwt"
        o_request = Request("/")
        o_request.user = user
        o_request.client = client
        o_request.scopes = scopes
        with request_context(rf.get("/")):
            token = generate_jwt_access_token(o_request)
        instance = Token(
            type=Token.Type.ACCESS_TOKEN,
            user=user,
            client=client,
            hash=get_adapter().hash_token(token),
        )
        instance.set_scopes(scopes)
        instance.save()
        return token, instance

    return f


@pytest.fixture
def opaque_access_token_factory():
    """Mint an *opaque* access token regardless of the parametrized format."""

    def f(client, user, scopes=["openid"], resources=None, expires_at=None):
        value = uuid.uuid4().hex
        instance = Token(
            type=Token.Type.ACCESS_TOKEN,
            user=user,
            client=client,
            hash=get_adapter().hash_token(value),
        )
        instance.set_scopes(scopes)
        if resources:
            instance.set_resources(resources)
        if expires_at:
            instance.expires_at = expires_at
        instance.save()
        return value, instance

    return f


# ---------------------------------------------------------------------------
# Caller authentication -- client credentials (client_secret_basic) mode
# ---------------------------------------------------------------------------


def test_introspect_client_credentials_basic(
    client, oidc_client, oidc_client_secret, user, access_token_factory
):
    """A confidential caller authenticating via Basic auth gets an active result."""
    token, _ = access_token_factory(oidc_client, user, scopes=["openid"])
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["active"] is True
    assert data["client_id"] == oidc_client.id
    assert data["iss"] == "http://testserver"


def test_introspect_wrong_client_secret_is_unauthorized(
    client, oidc_client, oidc_client_secret, user, access_token_factory
):
    token, _ = access_token_factory(oidc_client, user, scopes=["openid"])
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, "wrong-secret"),
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json()["error"] == "invalid_client"


def test_introspect_client_credentials_post_body(
    client, oidc_client, oidc_client_secret, user, access_token_factory
):
    """client_secret_post (credentials in the body) authenticates the caller too.

    Note: ``client_secret_post`` is reachable even though it is not in the
    view's ``supported_methods`` list -- only the bearer/basic/none paths are
    gated by that list.
    """
    token, _ = access_token_factory(oidc_client, user, scopes=["openid"])
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={
            "token": token,
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["active"] is True


# ---------------------------------------------------------------------------
# Target token results
# ---------------------------------------------------------------------------


def test_introspect_opaque_access_token_claims(
    client, oidc_client, oidc_client_secret, user, opaque_access_token_factory
):
    """An *opaque* access token gets a server-constructed RFC 7662 claim set."""
    expires_at = timezone.now() + timedelta(seconds=300)
    token, instance = opaque_access_token_factory(
        oidc_client,
        user,
        scopes=["openid", "profile"],
        resources=["https://api.example.com/a"],
        expires_at=expires_at,
    )
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["active"] is True
    assert data["token_type"] == "access_token"
    assert data["scope"] == "openid profile"
    assert data["iss"] == "http://testserver"
    assert data["client_id"] == oidc_client.id
    assert data["sub"] == get_adapter().get_user_sub(oidc_client, user)
    assert data["aud"] == ["https://api.example.com/a"]
    assert data["exp"] == int(instance.expires_at.timestamp())
    assert data["iat"] == int(instance.created_at.timestamp())


def test_introspect_jwt_access_token_claims(
    client, oidc_client, oidc_client_secret, user, jwt_access_token_factory
):
    """
    An *JWT* access token gets a server-constructed RFC 7662 claim set, matching the *opaque* case.
    Note: This is different from the token's own JWT claims -- see RFC 7662 section 4, which allows
          for a different response shape for JWT tokens, but the spec is permissive and allows for
          the same claim set as opaque tokens too.
    """
    token, instance = jwt_access_token_factory(
        oidc_client, user, scopes=["openid", "profile"]
    )
    instance.expires_at = timezone.now() + timedelta(seconds=300)
    instance.save()
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["active"] is True
    assert data["token_type"] == "access_token"
    assert data["scope"] == "openid profile"
    assert data["iss"] == "http://testserver"
    assert data["client_id"] == oidc_client.id
    assert data["sub"] == get_adapter().get_user_sub(oidc_client, user)
    assert data["exp"] == int(instance.expires_at.timestamp())


def test_introspect_active_refresh_token(
    client, oidc_client, oidc_client_secret, user, refresh_token_factory
):
    refresh_value, _ = refresh_token_factory(user=user, client=oidc_client)
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": refresh_value, "token_type_hint": "refresh_token"},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["active"] is True
    assert data["token_type"] == "refresh_token"


def test_introspect_expired_token_is_inactive(
    client, oidc_client, oidc_client_secret, user, access_token_factory
):
    token, instance = access_token_factory(oidc_client, user, scopes=["openid"])
    instance.expires_at = timezone.now() - timedelta(seconds=60)
    instance.save()
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"active": False}


def test_introspect_unknown_token_is_inactive(client, oidc_client, oidc_client_secret):
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": "does-not-exist"},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"active": False}


def test_introspect_token_type_hint_mismatch_falls_back(
    client, oidc_client, oidc_client_secret, user, refresh_token_factory
):
    """A wrong token_type_hint still resolves the token via the fallback type."""
    refresh_value, _ = refresh_token_factory(user=user, client=oidc_client)
    resp = client.post(
        reverse("idp:oidc:introspect"),
        # Wrong hint on purpose: the token is a refresh token.
        data={"token": refresh_value, "token_type_hint": "access_token"},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["active"] is True
    assert data["token_type"] == "refresh_token"


# ---------------------------------------------------------------------------
# Target token results -- JWT detection branch
# ---------------------------------------------------------------------------


def test_introspect_valid_jwt_token(
    client, oidc_client, oidc_client_secret, user, jwt_access_token_factory
):
    """A genuine JWT access token is detected and introspected as active."""
    token, _ = jwt_access_token_factory(oidc_client, user, scopes=["openid"])
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["active"] is True
    assert data["token_type"] == "access_token"


def test_introspect_invalid_jwt_token_is_inactive(
    client, oidc_client, oidc_client_secret
):
    """A JWT-shaped but undecodable token resolves to active: false."""
    # Starts with "ey" and has two dots, so it is treated as a JWT, but the
    # signature is bogus, so decoding fails -> token-not-active.
    bogus_jwt = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJ4In0.not-a-real-signature"
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": bogus_jwt},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {"active": False}


# ---------------------------------------------------------------------------
# Request validation
# ---------------------------------------------------------------------------


def test_introspect_missing_token_is_invalid_request(
    client, oidc_client, oidc_client_secret
):
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={},
        HTTP_AUTHORIZATION=_basic_auth(oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["error"] == "invalid_request"


@pytest.mark.parametrize("cross_client_allowed", [False, True])
def test_introspect_other_client(
    client,
    oidc_client,
    oidc_client_secret,
    oidc_client_factory,
    user,
    opaque_access_token_factory,
    cross_client_allowed,
    settings,
):
    """An *opaque* access token gets a server-constructed RFC 7662 claim set."""
    settings.IDP_OIDC_INTROSPECTION_CROSS_CLIENT_ALLOWED = cross_client_allowed
    token, instance = opaque_access_token_factory(
        oidc_client,
        user,
        scopes=["openid", "profile"],
        resources=["https://api.example.com/a"],
    )
    other_oidc_client = oidc_client_factory(secret=oidc_client_secret)
    resp = client.post(
        reverse("idp:oidc:introspect"),
        data={"token": token},
        HTTP_AUTHORIZATION=_basic_auth(other_oidc_client.id, oidc_client_secret),
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["active"] == cross_client_allowed
