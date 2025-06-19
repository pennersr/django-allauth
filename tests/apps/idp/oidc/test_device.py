from http import HTTPStatus
from unittest.mock import ANY

from django.core.cache import cache
from django.urls import reverse
from django.utils.http import urlencode

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.idp.oidc import app_settings
from allauth.idp.oidc.internal.oauthlib import device_codes
from allauth.idp.oidc.models import Client, Token


@pytest.fixture
def poll_sleep():
    def f(device_code, seconds):
        data = cache.get(device_codes.cache_device_code_key(device_code))
        if data:
            data["last_poll_at"] -= seconds
            device_codes.update_device_state(device_code, data)

    return f


def test_device_flow_invalid_client(
    db,
    client,
):
    payload = {
        "client_id": "unknown",
    }
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode(payload),
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_request",
        "error_description": "Invalid client_id parameter value.",
    }


def test_device_flow_invalid_scope(db, client, device_client):
    payload = {
        "client_id": device_client.id,
        "scope": "openid wrong",
    }
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode(payload),
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {"error": "invalid_scope"}


@pytest.mark.parametrize("action", ["deny", "confirm"])
@pytest.mark.parametrize("with_scope", [False, True])
def test_device_flow(
    client,
    auth_client,
    device_client,
    enable_cache,
    action,
    user,
    with_scope,
    poll_sleep,
):
    device_client.set_default_scopes(["profile"])
    device_client.save()
    payload = {
        "client_id": device_client.id,
    }
    if with_scope:
        payload["scope"] = " ".join(["openid", "email"])
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode(payload),
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data == {
        "verification_uri": "http://testserver/identity/o/device",
        "verification_uri_complete": ANY,
        "expires_in": app_settings.DEVICE_CODE_EXPIRES_IN,
        "user_code": ANY,
        "device_code": ANY,
        "interval": 5,
    }
    assert (
        data["verification_uri_complete"]
        == data["verification_uri"] + "?code=" + data["user_code"]
    )

    resp = client.post(
        reverse("idp:oidc:token"),
        {
            "device_code": data["device_code"],
            "grant_type": Client.GrantType.DEVICE_CODE,
            "client_id": device_client.id,
        },
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "authorization_pending",
    }

    resp = auth_client.get(data["verification_uri"])
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/device_authorization_code_form.html")
    assert resp.context["form"].errors == {}

    resp = auth_client.get(data["verification_uri"] + "?code=wrong")
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/device_authorization_code_form.html")
    assert resp.context["form"].errors == {"code": ["Incorrect code."]}

    resp = auth_client.get(data["verification_uri_complete"])
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/device_authorization_confirm_form.html")

    confirmed = action == "confirm"
    resp = auth_client.post(data["verification_uri_complete"], {"action": action})
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(
        resp,
        (
            "idp/oidc/device_authorization_confirmed.html"
            if confirmed
            else "idp/oidc/device_authorization_denied.html"
        ),
    )

    poll_sleep(data["device_code"], 10)
    resp = client.post(
        reverse("idp:oidc:token"),
        {
            "device_code": data["device_code"],
            "grant_type": Client.GrantType.DEVICE_CODE,
            "client_id": device_client.id,
        },
    )
    if confirmed:
        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "access_token": ANY,
            "expires_in": 3600,
            "refresh_token": ANY,
            "scope": "openid email" if with_scope else "profile",
            "token_type": "Bearer",
        }
        token = Token.objects.lookup(
            Token.Type.ACCESS_TOKEN, resp.json()["access_token"]
        )
        assert token.user_id == user.pk
        # Single-use device codes.
        poll_sleep(data["device_code"], 10)
        resp = client.post(
            reverse("idp:oidc:token"),
            {
                "device_code": data["device_code"],
                "grant_type": Client.GrantType.DEVICE_CODE,
                "client_id": device_client.id,
            },
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "error": "invalid_grant",
        }

    else:
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "error": "access_denied",
        }


def test_slow_down_flow(client, device_client, enable_cache, poll_sleep):
    payload = {
        "client_id": device_client.id,
    }
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode(payload),
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()

    for sleep, error in [
        (0, "authorization_pending"),
        (3, "slow_down"),
        (3, "authorization_pending"),
    ]:
        if sleep:
            poll_sleep(data["device_code"], sleep)
        resp = client.post(
            reverse("idp:oidc:token"),
            {
                "device_code": data["device_code"],
                "grant_type": Client.GrantType.DEVICE_CODE,
                "client_id": device_client.id,
            },
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {"error": error}
