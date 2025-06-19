from http import HTTPStatus
from unittest.mock import ANY

from django.urls import reverse

import pytest

from allauth.idp.oidc.models import Token


def test_userinfo_bad_token(client, oidc_client, user):
    # Pass along ID token as hint
    resp = client.get(reverse("idp:oidc:userinfo"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    assert resp.json() == {
        "error": "invalid_token",
        "error_description": "The access token provided is expired, revoked, malformed, or invalid for other reasons.",
    }


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


@pytest.mark.parametrize("rotate_refresh_token", [False, True])
@pytest.mark.parametrize("scopes", [("openid",), ("openid", "email")])
def test_refresh_token(
    db,
    client,
    oidc_client,
    oidc_client_secret,
    user,
    refresh_token_factory,
    settings,
    rotate_refresh_token,
    scopes,
):
    settings.IDP_OIDC_ROTATE_REFRESH_TOKEN = rotate_refresh_token
    rt, rt_instance = refresh_token_factory(
        user=user, client=oidc_client, scopes=scopes
    )
    rt_instance.set_scope_email("a@b.org")
    rt_instance.save()
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
    data = resp.json()
    new_rt_instance = Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, data["refresh_token"]
    )
    if rotate_refresh_token:
        assert data["refresh_token"] != rt
        assert new_rt_instance.pk != rt_instance.pk
    else:
        assert data["refresh_token"] == rt
    assert Token.objects.filter(type=Token.Type.REFRESH_TOKEN).count() == 1
    token = Token.objects.lookup(Token.Type.ACCESS_TOKEN, data["access_token"])

    assert token.get_scope_email() == ("a@b.org" if "email" in scopes else None)
    return
    assert data == {
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
