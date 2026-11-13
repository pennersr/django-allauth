import base64
from datetime import timedelta
from http import HTTPStatus
from unittest.mock import ANY, patch
from urllib.parse import parse_qs, urlparse

from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode

import jwt
import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.models import EmailAddress
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Token

from .internal.test_tokens import PREVIOUS_PRIVATE_KEY


@pytest.mark.parametrize(
    "scopes,has_secondary_email,choose_secondary_email",
    [
        (("openid",), False, False),
        (("openid", "email"), False, False),
        (("openid", "email"), True, True),
    ],
)
def test_userinfo(
    client,
    oidc_client,
    user,
    access_token_factory,
    scopes,
    has_secondary_email,
    choose_secondary_email,
    email_factory,
):
    # Pass along ID token as hint
    token, token_instance = access_token_factory(oidc_client, user, scopes=scopes)
    if has_secondary_email:
        email = email_factory()
        EmailAddress.objects.create(
            user=user, email=email, verified=True, primary=False
        )
        token_instance.set_scope_email(email)
        token_instance.save()
        expected_email = email if choose_secondary_email else user.email
    else:
        expected_email = user.email
    resp = client.get(
        reverse("idp:oidc:userinfo"),
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["sub"] == get_adapter().get_user_sub(oidc_client, user)
    if "email" in scopes:
        assert data["email"] == expected_email
        assert data["email_verified"] is True
    else:
        assert "email" not in data


@pytest.mark.parametrize(
    "resources",
    [
        [],
        ["https://api.example.com/a"],
        ["https://api.example.com/a", "https://api.example.com/b"],
    ],
)
@pytest.mark.parametrize("access_token_format", ["jwt", "opaque"])
@pytest.mark.parametrize("basic_auth", (False, True))
def test_client_credentials(
    client,
    oidc_client,
    oidc_client_secret,
    access_token_format,
    settings,
    basic_auth,
    resources,
):
    settings.IDP_OIDC_ACCESS_TOKEN_FORMAT = access_token_format
    data = {
        "scope": "profile email",
        "grant_type": "client_credentials",
    }
    if resources:
        data["resource"] = resources

    post_kwargs = {}
    if not basic_auth:
        data.update(
            {
                "client_id": oidc_client.id,
                "client_secret": oidc_client_secret,
            }
        )
    else:
        credentials = base64.b64encode(
            f"{oidc_client.id}:{oidc_client_secret}".encode()
        ).decode()
        post_kwargs = {"HTTP_AUTHORIZATION": f"Basic {credentials}"}

    resp = client.post(reverse("idp:oidc:token"), data=data, **post_kwargs)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data == {
        "access_token": ANY,
        "expires_in": 3600,
        "scope": "profile email",
        "token_type": "Bearer",
    }
    token = Token.objects.lookup(Token.Type.ACCESS_TOKEN, data["access_token"])
    assert token.client == oidc_client
    assert token.get_scopes() == ["profile", "email"]
    assert set(token.get_resources()) == set(resources)

    if access_token_format == "jwt":
        decoded = jwt.decode(data["access_token"], options={"verify_signature": False})
        expected_decoded = {
            "client_id": oidc_client.id,
            "exp": ANY,
            "iat": ANY,
            "iss": "http://testserver",
            "jti": ANY,
            "scope": "profile email",
            "token_use": "access",
        }
        if resources:
            expected_decoded["aud"] = resources
        assert decoded == expected_decoded


def test_client_secret_basic_invalid(client, oidc_client):
    credentials = base64.b64encode(f"{oidc_client.id}:wrong-secret".encode()).decode()
    resp = client.post(
        reverse("idp:oidc:token"),
        data={
            "scope": "profile",
            "grant_type": "client_credentials",
        },
        HTTP_AUTHORIZATION=f"Basic {credentials}",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_password_grant_is_blocked(
    client, oidc_client, oidc_client_secret, user, user_password
):
    resp = client.post(
        reverse("idp:oidc:token"),
        data={
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            # These are valid credentials.
            "username": user.username,
            "password": user_password,
            "scope": "profile email",
            "grant_type": "password",
        },
    )
    # We don't crash, but also don't grant.
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_grant",
        "error_description": "Invalid credentials given.",
    }


@pytest.mark.parametrize(
    "resources",
    [
        [],
        ["https://api.example.com/a"],
        ["https://api.example.com/a", "https://api.example.com/b"],
    ],
)
def test_implicit_grant_flow(auth_client, user, oidc_client, enable_cache, resources):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    scopes = ["openid", "profile"]
    data = {
        "client_id": oidc_client.id,
        "response_type": "token",
        "scope": " ".join(scopes),
        "nonce": "some-nonce",
        "state": "some-state",
        "redirect_uri": redirect_uri,
    }
    if resources:
        data["resource"] = resources
    resp = auth_client.get(
        reverse("idp:oidc:authorization") + "?" + urlencode(data, doseq=True)
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
        {
            "scopes": scopes,
            "action": "grant",
            "request": resp.context["form"]["request"].value(),
        },
    )
    # "https://client/callback#access_token=baI5uc9m5JWc6afKqaZ9eymeOrq1hz&expires_in=3600&token_type=Bearer&scope=openid+profile&state=some-state"
    assert resp.status_code == HTTPStatus.FOUND
    parts = urlparse(resp["location"])
    data = parse_qs(parts.fragment)
    assert data == {
        "access_token": ANY,
        "expires_in": ["3600"],
        "scope": ["openid profile"],
        "token_type": ["Bearer"],
        "state": ["some-state"],
    }
    token = Token.objects.lookup(Token.Type.ACCESS_TOKEN, data["access_token"][0])
    assert set(token.get_resources()) == set(resources)


def test_userinfo_access_token_as_query(
    client, oidc_client, user, access_token_factory
):
    # Pass along ID token as hint
    token, _ = access_token_factory(oidc_client, user, scopes=["openid"])
    resp = client.get(
        f"{reverse('idp:oidc:userinfo')}?{urlencode({'access_token': token})}",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_jwks_view(client, settings):
    settings.IDP_OIDC_JWKS_CACHE_CONTROL = 4711
    resp = client.get(reverse("idp:oidc:jwks"))
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "keys": [{"e": ANY, "key_ops": ["verify"], "kid": ANY, "kty": "RSA", "n": ANY}]
    }
    assert resp["Cache-Control"] == "max-age=4711, must-revalidate"


@pytest.mark.parametrize("expires_in,key_count", [(-60, 1), (60, 2)])
def test_jwks_view_skips_expired_keys(client, settings, key_count, expires_in):
    settings.USE_TZ = True
    settings.IDP_OIDC_PRIVATE_KEYS = [
        {
            "pem": PREVIOUS_PRIVATE_KEY,
            "expires_at": timezone.now() + timedelta(seconds=expires_in),
        }
    ]
    resp = client.get(reverse("idp:oidc:jwks"))
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "keys": [{"e": ANY, "key_ops": ["verify"], "kid": ANY, "kty": "RSA", "n": ANY}]
        * key_count,
    }


@pytest.mark.parametrize("expires_in,expected_max_age", [(90, 90), (10000, 4711)])
def test_jwks_view_clamps_cache_control(client, settings, expires_in, expected_max_age):
    settings.USE_TZ = True
    settings.IDP_OIDC_JWKS_CACHE_CONTROL = 4711
    now = timezone.now()
    settings.IDP_OIDC_PRIVATE_KEYS = [
        {
            "pem": PREVIOUS_PRIVATE_KEY,
            "expires_at": now + timedelta(seconds=expires_in),
        }
    ]
    # Pin the adapter's clock so the clamp is exact; an expiry sooner than the
    # configured max-age must shorten it, a later one must leave it untouched.
    with patch("allauth.idp.oidc.adapter.timezone.now", return_value=now):
        resp = client.get(reverse("idp:oidc:jwks"))
    assert resp.status_code == HTTPStatus.OK
    assert resp["Cache-Control"] == f"max-age={expected_max_age}, must-revalidate"


@pytest.mark.parametrize("custom_userinfo_endpoint", [False, True])
def test_configuration_view(
    client, oidc_client, custom_userinfo_endpoint, settings_impacting_urls
):
    with settings_impacting_urls(
        IDP_OIDC_INTROSPECTION_ENABLED=True,
        IDP_OIDC_USERINFO_ENDPOINT=(
            "https://remote/userinfo" if custom_userinfo_endpoint else None
        ),
    ):
        resp = client.get(reverse("idp:oidc:configuration"))
        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "authorization_endpoint": "http://testserver/identity/o/authorize",
            "device_authorization_endpoint": "http://testserver/identity/o/api/device/code",
            "end_session_endpoint": "http://testserver/identity/o/logout",
            "id_token_signing_alg_values_supported": ["RS256"],
            "issuer": "http://testserver",
            "jwks_uri": "http://testserver/.well-known/jwks.json",
            "response_types_supported": [
                "code",
                "code id_token",
                "code id_token token",
                "code token",
                "id_token",
                "id_token token",
                "none",
                "token",
            ],
            "revocation_endpoint": "http://testserver/identity/o/api/revoke",
            "introspection_endpoint": "http://testserver/identity/o/api/introspect",
            "introspection_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
            ],
            "subject_types_supported": ["public"],
            "token_endpoint": "http://testserver/identity/o/api/token",
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post",
                "none",
            ],
            "scopes_supported": ["openid", "profile", "email"],
            "userinfo_endpoint": (
                "https://remote/userinfo"
                if custom_userinfo_endpoint
                else "http://testserver/identity/o/api/userinfo"
            ),
            "code_challenge_methods_supported": ["S256"],
            "grant_types_supported": [
                "authorization_code",
                "client_credentials",
                "refresh_token",
                "urn:ietf:params:oauth:grant-type:device_code",
            ],
        }


def test_configuration_view_without_introspection(
    client, oidc_client, settings_impacting_urls
):
    with settings_impacting_urls(IDP_OIDC_INTROSPECTION_ENABLED=False):
        resp = client.get(reverse("idp:oidc:configuration"))
        assert resp.status_code == HTTPStatus.OK
        data = resp.json()
        assert "introspection_endpoint" not in data
        assert "introspection_endpoint_auth_methods_supported" not in data


def test_configuration_view_with_custom_scopes(
    client, settings, settings_impacting_urls
):
    settings.IDP_OIDC_SCOPE_CHOICES = [
        "openid",
        ("mcp", "Use the MCP server"),
    ]
    with settings_impacting_urls():
        response = client.get(reverse("idp:oidc:configuration"))

    assert response.json()["scopes_supported"] == ["openid", "mcp"]


def test_post_userinfo(
    client,
    oidc_client,
    user,
    access_token_factory,
):
    # Pass along ID token as hint
    token, token_instance = access_token_factory(oidc_client, user)
    resp = client.post(
        reverse("idp:oidc:userinfo"),
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["sub"] == get_adapter().get_user_sub(oidc_client, user)
