from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

from django.test import Client
from django.urls import reverse
from django.utils.http import urlencode

import jwt
import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.socialaccount.providers.oauth2.utils import (
    generate_code_challenge,
)


def test_cancel_authorization(auth_client, oidc_client):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
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
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
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
        reverse("idp:oidc:authorization")
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
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
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
        reverse("idp:oidc:authorization")
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


def test_authorization_id_token_hint_match(
    user, id_token_generator, oidc_client, auth_client, user_factory
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    # Pass along ID token as hint
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
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


def test_authorization_id_token_hint_mismatch(
    user, id_token_generator, oidc_client, auth_client, user_factory
):
    redirect_uri = oidc_client.get_redirect_uris()[0]
    # Pass along ID token as hint
    resp = auth_client.get(
        reverse("idp:oidc:authorization")
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


def test_authorization_post_redirects_to_get(auth_client):
    payload = {
        "client_id": "c123",
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    resp = auth_client.post(reverse("idp:oidc:authorization"), data=payload)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("idp:oidc:authorization") + "?" + urlencode(
        payload
    )


def test_authorization_post_redirects_anon_to_get(db, client):
    payload = {
        "client_id": "c123",
        "response_type": "code",
        "scope": "openid",
        "nonce": "some-nonce",
        "state": "some-state",
    }
    resp = client.post(reverse("idp:oidc:authorization"), data=payload, follow=True)
    assert resp.status_code == HTTPStatus.OK
    url = reverse("idp:oidc:authorization") + "?" + urlencode(payload)
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
    resp = client.post(reverse("idp:oidc:authorization"), data=payload)
    assert resp.status_code == HTTPStatus.FORBIDDEN
    assert b"CSRF Failed" in resp.content


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
        reverse("idp:oidc:authorization")
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
    assertTemplateUsed(resp, "idp/oidc/authorization_form.html")
    resp = auth_client.post(
        reverse("idp:oidc:authorization"),
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
