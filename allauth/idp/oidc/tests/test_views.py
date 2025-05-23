from http import HTTPStatus
from unittest.mock import ANY
from urllib.parse import parse_qs, urlparse

from django.urls import reverse
from django.utils.http import urlencode

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.models import EmailAddress
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Token


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
    access_token_generator,
    scopes,
    has_secondary_email,
    choose_secondary_email,
    email_factory,
):
    # Pass along ID token as hint
    token, token_instance = access_token_generator(oidc_client, user, scopes=scopes)
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
        reverse("idp:oidc:authorization")
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


def test_userinfo_access_token_as_query(
    client, oidc_client, user, access_token_generator
):
    # Pass along ID token as hint
    token, _ = access_token_generator(oidc_client, user, scopes=["openid"])
    resp = client.get(
        reverse("idp:oidc:userinfo") + "?" + urlencode({"access_token": token}),
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


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
        "authorization_endpoint": "http://testserver/identity/o/authorize",
        "id_token_signing_alg_values_supported": ["RS256"],
        "issuer": "http://testserver",
        "jwks_uri": "http://testserver/.well-known/jwks.json",
        "response_types_supported": ["code", "token"],
        "revocation_endpoint": "http://testserver/identity/o/api/revoke",
        "subject_types_supported": ["public"],
        "token_endpoint": "http://testserver/identity/o/api/token",
        "userinfo_endpoint": "http://testserver/identity/o/api/userinfo",
    }
