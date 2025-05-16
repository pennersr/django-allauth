from http import HTTPStatus
from unittest.mock import ANY
from urllib.parse import parse_qs, urlparse

from django.test import Client
from django.urls import reverse
from django.utils.http import urlencode

import jwt
import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Token
from allauth.socialaccount.providers.oauth2.utils import (
    generate_code_challenge,
)


def test_cancel_authorization(auth_client, oidc_client):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/openid_connect/authorize_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorize"),
        {
            "request": resp.context["form"]["request"].value(),
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == f"{redirect_uri}?error=access_denied"


@pytest.mark.parametrize(
    "scopes",
    [
        ("openid", "profile", "email"),
        ("openid", "profile"),
        ("openid",),
    ],
)
def test_authorization_code_flow(
    auth_client, user, oidc_client, oidc_client_secret, enable_cache, scopes
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "nonce": "some-nonce",
                "state": "some-state",
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/openid_connect/authorize_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorize"),
        {
            "scopes": scopes,
            "action": "grant",
            "request": resp.context["form"]["request"].value(),
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirected_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    assert params["state"][0] == "some-state"
    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data.keys()) == {
        "access_token",
        "expires_in",
        "token_type",
        "scope",
        "refresh_token",
        "id_token",
    }

    # ID token
    id_token = data["id_token"]
    decoded = jwt.decode(id_token, options={"verify_signature": False})
    assert decoded["sub"] == str(user.pk)
    assert decoded["nonce"] == "some-nonce"
    if "email" in scopes:
        assert decoded["email"] == user.email
    else:
        assert "email" not in decoded
    if "profile" in scopes:
        assert decoded["preferred_username"] == user.username
    else:
        assert "preferred_username" not in decoded


def test_authorization_code_flow_skip_consent(
    auth_client, user, oidc_client, oidc_client_secret, enable_cache
):
    oidc_client.skip_consent = True
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "code",
                "scope": "openid profile email",
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirect_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "redirect_uri": redirect_uri,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data.keys()) == {
        "access_token",
        "expires_in",
        "token_type",
        "scope",
        "refresh_token",
        "id_token",
    }


def test_authorize_id_token_hint_match(
    user, id_token_generator, oidc_client, auth_client, user_factory
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    # Pass along ID token as hint
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "id_token_hint": id_token_generator(oidc_client, user),
                "response_type": "code",
                "scope": "openid",
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK


def test_authorize_id_token_hint_mismatch(
    user, id_token_generator, oidc_client, auth_client, user_factory
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    # Pass along ID token as hint
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "id_token_hint": id_token_generator(oidc_client, user_factory()),
                "response_type": "code",
                "redirect_uri": redirect_uri,
                "scope": "openid",
                "nonce": "some-nonce",
                "state": "some-state",
            }
        )
    )
    assert resp.status_code == HTTPStatus.FOUND
    parts = urlparse(resp["location"])
    params = parse_qs(parts.query)
    assert params["error"] == ["login_required"]
    assert params["error_description"] == [
        "Session user does not match client supplied user."
    ]


def test_userinfo_bad_token(client, oidc_client, user):
    # Pass along ID token as hint
    resp = client.get(reverse("idp:oidc:userinfo"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json() == {
        "error": "invalid_token",
        "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons.",
    }


@pytest.mark.parametrize("scopes", [("openid",), ("openid", "email")])
def test_userinfo(client, oidc_client, user, access_token_generator, scopes):
    # Pass along ID token as hint
    token, _ = access_token_generator(oidc_client, user, scopes=scopes)
    resp = client.get(
        reverse("idp:oidc:userinfo"),
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["sub"] == get_adapter().get_user_sub(oidc_client, user)
    if "email" in scopes:
        assert data["email"] == user.email
        assert data["email_verified"] is True
    else:
        assert "email" not in data


def test_revoke_access_token(
    client, oidc_client, oidc_client_secret, user, access_token_generator
):
    token, instance = access_token_generator(oidc_client, user)
    _, instance_to_keep = access_token_generator(oidc_client, user)
    resp = client.post(
        reverse("idp:oidc:revoke"),
        data={
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "token": token,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    assert not Token.objects.filter(pk=instance.pk).exists()
    assert Token.objects.filter(pk=instance_to_keep.pk).exists()


def test_client_credentials(client, oidc_client, oidc_client_secret):
    resp = client.post(
        reverse("idp:oidc:token"),
        data={
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
            "scope": "profile email",
            "grant_type": "client_credentials",
        },
    )
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
    assert resp.status_code == 400
    assert resp.json() == {
        "error": "invalid_grant",
        "error_description": "Invalid credentials given.",
    }


def test_implicit_grant_flow(auth_client, user, oidc_client, enable_cache):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    scopes = ["openid", "profile"]
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "response_type": "token",
                "scope": " ".join(scopes),
                "nonce": "some-nonce",
                "state": "some-state",
                "redirect_uri": redirect_uri,
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/openid_connect/authorize_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorize"),
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


def test_userinfo_access_token_as_query(
    client, oidc_client, user, access_token_generator
):
    # Pass along ID token as hint
    token, _ = access_token_generator(oidc_client, user, scopes=["openid"])
    resp = client.get(
        reverse("idp:oidc:userinfo") + "?" + urlencode({"access_token": token}),
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_authorization_post_redirects_to_get(auth_client):
    payload = {
        "client_id": "c123",
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    resp = auth_client.post(reverse("idp:oidc:authorize"), data=payload)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("idp:oidc:authorize") + "?" + urlencode(payload)


def test_authorization_post_redirects_anon_to_get(db, client):
    payload = {
        "client_id": "c123",
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    resp = client.post(reverse("idp:oidc:authorize"), data=payload, follow=True)
    assert resp.status_code == HTTPStatus.OK
    url = reverse("idp:oidc:authorize") + "?" + urlencode(payload)
    assert resp.redirect_chain == [
        (url, HTTPStatus.FOUND),
        (
            reverse("account_login")
            + "?"
            + urlencode({"next": url}).replace("%2F", "/"),
            HTTPStatus.FOUND,
        ),
    ]


def test_authorization_post_is_csrf_protected(user):
    client = Client(enforce_csrf_checks=True)
    client.force_login(user)
    payload = {
        "request": "dummy",
        "scopes": "openid",
    }
    resp = client.post(reverse("idp:oidc:authorize"), data=payload)
    assert resp.status_code == HTTPStatus.FORBIDDEN
    assert b"CSRF Failed" in resp.content


def test_refresh_token(
    db, client, oidc_client, oidc_client_secret, user, refresh_token_factory
):
    rt, _ = refresh_token_factory(user=user, client=oidc_client)
    resp = client.post(
        reverse("idp:oidc:token"),
        {
            "refresh_token": rt,
            "grant_type": "refresh_token",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "access_token": ANY,
        "expires_in": 3600,
        "refresh_token": ANY,
        "scope": "openid profile",
        "token_type": "Bearer",
    }


def test_revoke_refresh_token(
    db, client, oidc_client, oidc_client_secret, user, refresh_token_factory
):
    token_value, token_instance = refresh_token_factory(user=user, client=oidc_client)
    resp = client.post(
        reverse("idp:oidc:revoke"),
        {
            "token": token_value,
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    assert resp.content == b""
    assert not Token.objects.filter(pk=token_instance.pk).exists()


def test_jwks_view(client):
    resp = client.get(reverse("idp:oidc:jwks"))
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "keys": [{"e": ANY, "key_ops": ["verify"], "kid": ANY, "kty": "RSA", "n": ANY}]
    }


def test_configuration_view(client, oidc_client):
    resp = client.get(reverse("idp:oidc:configuration"))
    assert resp.status_code == HTTPStatus.OK
    assert resp.json() == {
        "authorization_endpoint": "http://testserver/identity/oidc/authorize",
        "id_token_signing_alg_values_supported": ["RS256"],
        "issuer": "http://testserver",
        "jwks_uri": "http://testserver/.well-known/jwks.json",
        "response_types_supported": ["code", "token"],
        "revocation_endpoint": "http://testserver/identity/oidc/revoke",
        "subject_types_supported": ["public"],
        "token_endpoint": "http://testserver/identity/oidc/token",
        "userinfo_endpoint": "http://testserver/identity/oidc/userinfo",
    }


@pytest.mark.parametrize("valid_code_verifier", [False, True])
def test_authorization_code_flow_with_pkce(
    auth_client,
    user,
    oidc_client,
    enable_cache,
    valid_code_verifier,
):
    oidc_client.type = oidc_client.Type.PUBLIC
    oidc_client.save()
    redirect_uri = oidc_client.get_redirect_uris()[0]
    scopes = ["openid", "profile", "email"]
    pkce = generate_code_challenge()
    resp = auth_client.get(
        reverse("idp:oidc:authorize")
        + "?"
        + urlencode(
            {
                "client_id": oidc_client.id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(scopes),
                "nonce": "some-nonce",
                "state": "some-state",
                "code_challenge": pkce["code_challenge"],
                "code_challenge_method": pkce["code_challenge_method"],
            }
        )
    )
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/openid_connect/authorize_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorize"),
        {
            "scopes": scopes,
            "action": "grant",
            "request": resp.context["form"]["request"].value(),
        },
    )
    assert resp.status_code == HTTPStatus.FOUND
    redirected_uri = resp["location"]
    assert redirected_uri.startswith(redirected_uri)
    parts = urlparse(redirected_uri)
    params = parse_qs(parts.query)
    code = params["code"][0]
    assert params["state"][0] == "some-state"
    resp = auth_client.post(
        reverse("idp:oidc:token"),
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": oidc_client.id,
            "redirect_uri": redirect_uri,
            "state": "some-state",
            "code_verifier": pkce["code_verifier"] if valid_code_verifier else "WRONG",
        },
    )
    if not valid_code_verifier:
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        return

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert set(data.keys()) == {
        "access_token",
        "expires_in",
        "id_token",
        "token_type",
        "scope",
        "refresh_token",
    }
