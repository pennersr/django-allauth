from http import HTTPStatus
from unittest.mock import ANY

from django.urls import reverse

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
