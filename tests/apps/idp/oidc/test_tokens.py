from datetime import timedelta
from http import HTTPStatus
from unittest.mock import ANY

from django.urls import reverse
from django.utils import timezone

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
    client, oidc_client, oidc_client_secret, user, access_token_factory
):
    token, instance = access_token_factory(oidc_client, user)
    _, instance_to_keep = access_token_factory(oidc_client, user)
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


@pytest.mark.parametrize("token_type", ["access", "refresh"])
def test_revoke_token_is_bound_to_client(
    client,
    oidc_client,
    oidc_client_secret,
    oidc_client_factory,
    user,
    access_token_factory,
    refresh_token_factory,
    token_type,
):
    if token_type == "access":
        token_value, token_instance = access_token_factory(oidc_client, user)
    else:
        token_value, token_instance = refresh_token_factory(
            user=user, client=oidc_client
        )
    other_client = oidc_client_factory()

    resp = client.post(
        reverse("idp:oidc:revoke"),
        data={
            "client_id": other_client.id,
            "client_secret": oidc_client_secret,
            "token": token_value,
        },
    )

    assert resp.status_code == HTTPStatus.OK
    assert Token.objects.filter(pk=token_instance.pk).exists()


@pytest.mark.parametrize(
    "resources",
    [
        [],
        ["https://api.example.com/a"],
        ["https://api.example.com/a", "https://api.example.com/b"],
    ],
)
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
    resources,
):
    settings.IDP_OIDC_ROTATE_REFRESH_TOKEN = rotate_refresh_token
    rt, rt_instance = refresh_token_factory(
        user=user, client=oidc_client, scopes=scopes
    )
    rt_instance.set_scope_email("a@b.org")
    rt_instance.save()
    data = {
        "refresh_token": rt,
        "grant_type": "refresh_token",
        "client_id": oidc_client.id,
        "client_secret": oidc_client_secret,
    }
    if resources:
        data["resource"] = resources
    resp = client.post(reverse("idp:oidc:token"), data)

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
    assert set(token.get_resources()) == set(resources)
    assert token.get_scope_email() == ("a@b.org" if "email" in scopes else None)
    return
    assert data == {
        "access_token": ANY,
        "expires_in": 3600,
        "refresh_token": ANY,
        "scope": "openid profile",
        "token_type": "Bearer",
    }


@pytest.mark.parametrize("rotate_refresh_token", [False, True])
@pytest.mark.parametrize("refresh_token_expires_in", [None, 3600])
def test_refresh_token_expiry(
    db,
    client,
    oidc_client,
    oidc_client_secret,
    user,
    refresh_token_factory,
    settings,
    rotate_refresh_token,
    refresh_token_expires_in,
):
    settings.IDP_OIDC_ROTATE_REFRESH_TOKEN = rotate_refresh_token
    settings.IDP_OIDC_REFRESH_TOKEN_EXPIRES_IN = refresh_token_expires_in
    rt, rt_instance = refresh_token_factory(user=user, client=oidc_client)
    if refresh_token_expires_in is None:
        # Tokens issued while expiry is disabled do not expire.
        rt_instance.expires_at = None
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
    new_rt = Token.objects.lookup(Token.Type.REFRESH_TOKEN, data["refresh_token"])
    if rotate_refresh_token:
        assert new_rt.pk != rt_instance.pk
        if refresh_token_expires_in:
            # Rotation mints a fresh token carrying a full expiry window
            # (sliding window), exposed as ``refresh_expires_in``.
            expected = timezone.now() + timedelta(seconds=refresh_token_expires_in)
            assert abs((new_rt.expires_at - expected).total_seconds()) < 30
            assert abs(data["refresh_expires_in"] - refresh_token_expires_in) < 30
        else:
            assert new_rt.expires_at is None
            assert "refresh_expires_in" not in data
    else:
        # The refresh token is reused as is: its expiry is not extended, and
        # ``refresh_expires_in`` reflects the remaining lifetime (the factory
        # issues tokens that expire in 60 seconds).
        assert new_rt.pk == rt_instance.pk
        assert new_rt.expires_at == rt_instance.expires_at
        if refresh_token_expires_in:
            assert 0 < data["refresh_expires_in"] <= 60
        else:
            assert "refresh_expires_in" not in data


def test_refresh_token_reuse_keeps_legacy_token_unexpiring(
    db, client, oidc_client, oidc_client_secret, user, refresh_token_factory, settings
):
    # Tokens issued before ``REFRESH_TOKEN_EXPIRES_IN`` was enabled are not
    # retroactively expired when rotation is off: the token is reused as is.
    settings.IDP_OIDC_ROTATE_REFRESH_TOKEN = False
    settings.IDP_OIDC_REFRESH_TOKEN_EXPIRES_IN = 3600
    rt, rt_instance = refresh_token_factory(user=user, client=oidc_client)
    rt_instance.expires_at = None
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
    assert data["refresh_token"] == rt
    rt_instance.refresh_from_db()
    assert rt_instance.expires_at is None
    assert "refresh_expires_in" not in data


def test_refresh_token_expired(
    db, client, oidc_client, oidc_client_secret, user, refresh_token_factory
):
    rt, rt_instance = refresh_token_factory(user=user, client=oidc_client)
    rt_instance.expires_at = timezone.now() - timedelta(seconds=1)
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
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["error"] == "invalid_grant"


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


@pytest.mark.parametrize("rotate_refresh_token", [False, True])
def test_revoke_refresh_token_revokes_access_tokens_from_same_grant(
    client,
    oidc_client,
    oidc_client_secret,
    user,
    access_token_factory,
    refresh_token_factory,
    settings,
    rotate_refresh_token,
):
    settings.IDP_OIDC_ROTATE_REFRESH_TOKEN = rotate_refresh_token
    refresh_token, _ = refresh_token_factory(user=user, client=oidc_client)
    _, unrelated_access_instance = access_token_factory(oidc_client, user)
    resp = client.post(
        reverse("idp:oidc:token"),
        {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    token_data = resp.json()
    access_token = token_data["access_token"]
    access_instance = Token.objects.lookup(Token.Type.ACCESS_TOKEN, access_token)
    assert access_instance is not None
    refresh_token = token_data["refresh_token"]
    refresh_instance = Token.objects.lookup(Token.Type.REFRESH_TOKEN, refresh_token)
    assert refresh_instance is not None
    assert access_instance.get_grant_id() == refresh_instance.get_grant_id()
    resp = client.get(
        reverse("idp:oidc:userinfo"),
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )
    assert resp.status_code == HTTPStatus.OK

    resp = client.post(
        reverse("idp:oidc:revoke"),
        {
            "token": refresh_token,
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
        },
    )

    assert resp.status_code == HTTPStatus.OK
    assert not Token.objects.filter(pk=refresh_instance.pk).exists()
    assert not Token.objects.filter(pk=access_instance.pk).exists()
    assert Token.objects.filter(pk=unrelated_access_instance.pk).exists()
    resp = client.get(
        reverse("idp:oidc:userinfo"),
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_revoke_refresh_token_with_wrong_type_hint(
    db, client, oidc_client, oidc_client_secret, user, refresh_token_factory
):
    """A wrong token_type_hint does not revoke when no matching token type exists."""
    token_value, token_instance = refresh_token_factory(user=user, client=oidc_client)
    resp = client.post(
        reverse("idp:oidc:revoke"),
        {
            "token": token_value,
            # Wrong hint on purpose: the token is a refresh token.
            "token_type_hint": "access_token",
            "client_id": oidc_client.id,
            "client_secret": oidc_client_secret,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    assert Token.objects.filter(pk=token_instance.pk).exists()


@pytest.mark.parametrize(
    "auth_resources,token_resources,success",
    [
        ([], ["https://api.example.com/a"], True),
        (["https://api.example.com"], ["https://api.example.com/a"], True),
        (["https://api.example.org"], ["https://api.example.com/a"], False),
        (
            ["https://api.example.org", "https://api.example.com"],
            ["https://api.example.com/a"],
            True,
        ),
        (["https://api.example.com/a"], ["https://api.example.com/b"], False),
    ],
)
def test_refresh_resource_vs_subresource(
    db,
    client,
    oidc_client,
    oidc_client_secret,
    user,
    refresh_token_factory,
    settings,
    auth_resources,
    token_resources,
    success,
):
    scopes = ["openid"]
    rt, rt_instance = refresh_token_factory(
        user=user, client=oidc_client, scopes=scopes
    )
    rt_instance.set_scope_email("a@b.org")
    rt_instance.set_resources(auth_resources)
    rt_instance.save()
    data = {
        "refresh_token": rt,
        "grant_type": "refresh_token",
        "client_id": oidc_client.id,
        "client_secret": oidc_client_secret,
    }
    if token_resources:
        data["resource"] = token_resources
    resp = client.post(reverse("idp:oidc:token"), data)

    if success:
        assert resp.status_code == HTTPStatus.OK
        data = resp.json()
        refresh_token = Token.objects.lookup(
            Token.Type.REFRESH_TOKEN, data["refresh_token"]
        )
        access_token = Token.objects.lookup(
            Token.Type.ACCESS_TOKEN, data["access_token"]
        )
        assert set(refresh_token.get_resources()) == set(auth_resources)
        assert set(access_token.get_resources()) == set(token_resources)
    else:
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        data = resp.json()
        assert data == {
            "error": "invalid_target",
            "error_description": "The requested resource is invalid, missing, unknown, or malformed.",
        }
