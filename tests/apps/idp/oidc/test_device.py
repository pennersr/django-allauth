from datetime import timedelta
from http import HTTPStatus
from unittest.mock import ANY

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
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
@pytest.mark.parametrize(
    "resources",
    [
        [],
        ["https://api.example.com/a"],
        ["https://api.example.com/a", "https://api.example.com/b"],
    ],
)
def test_device_flow(
    client,
    auth_client,
    device_client,
    enable_cache,
    action,
    user,
    with_scope,
    poll_sleep,
    resources,
):
    device_client.set_default_scopes(["profile"])
    device_client.save()
    payload = {
        "client_id": device_client.id,
    }
    if with_scope:
        payload["scope"] = "openid email"
    if resources:
        payload["resource"] = resources
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode(payload, doseq=True),
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
        "scope": "openid email" if with_scope else "profile",
    }
    assert (
        data["verification_uri_complete"]
        == f"{data['verification_uri']}?code={data['user_code']}"
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

    resp = auth_client.get(f"{data['verification_uri']}?code=wrong")
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
        assert set(token.get_resources()) == set(resources)
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


def test_device_flow_refresh_token_expiry(
    client,
    auth_client,
    device_client,
    enable_cache,
    user,
    poll_sleep,
    settings,
):
    # The refresh token issued by the device grant carries the configured
    # expiry, exposed in the token response as ``refresh_expires_in``.
    settings.IDP_OIDC_REFRESH_TOKEN_EXPIRES_IN = 3600
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode({"client_id": device_client.id, "scope": "openid"}),
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    resp = auth_client.get(data["verification_uri_complete"])
    assert resp.status_code == HTTPStatus.OK
    resp = auth_client.post(data["verification_uri_complete"], {"action": "confirm"})
    assert resp.status_code == HTTPStatus.OK
    poll_sleep(data["device_code"], 10)
    resp = client.post(
        reverse("idp:oidc:token"),
        {
            "device_code": data["device_code"],
            "grant_type": Client.GrantType.DEVICE_CODE,
            "client_id": device_client.id,
        },
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert abs(data["refresh_expires_in"] - 3600) < 30
    refresh_token = Token.objects.lookup(
        Token.Type.REFRESH_TOKEN, data["refresh_token"]
    )
    expected = timezone.now() + timedelta(seconds=3600)
    assert abs((refresh_token.expires_at - expected).total_seconds()) < 30


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


@pytest.mark.parametrize(
    "granted_resources,requested_resources,success",
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
def test_device_flow_requested_vs_granted_resources(
    client,
    auth_client,
    device_client,
    enable_cache,
    user,
    poll_sleep,
    granted_resources,
    requested_resources,
    success,
):
    device_client.set_default_scopes(["profile"])
    device_client.save()
    payload = {
        "client_id": device_client.id,
        "scope": "openid email",
    }
    if granted_resources:
        payload["resource"] = granted_resources
    resp = client.post(
        reverse("idp:oidc:device_code"),
        data=urlencode(payload, doseq=True),
        content_type="application/x-www-form-urlencoded",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()

    resp = auth_client.get(data["verification_uri"])
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/device_authorization_code_form.html")
    assert resp.context["form"].errors == {}

    resp = auth_client.get(data["verification_uri_complete"])
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "idp/oidc/device_authorization_confirm_form.html")

    resp = auth_client.post(data["verification_uri_complete"], {"action": "confirm"})
    assert resp.status_code == HTTPStatus.OK
    poll_sleep(data["device_code"], 10)
    data = {
        "device_code": data["device_code"],
        "grant_type": Client.GrantType.DEVICE_CODE,
        "client_id": device_client.id,
    }
    if requested_resources:
        data["resource"] = requested_resources
    resp = client.post(
        reverse("idp:oidc:token"),
        data,
    )
    if success:
        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {
            "access_token": ANY,
            "expires_in": 3600,
            "refresh_token": ANY,
            "scope": "openid email",
            "token_type": "Bearer",
        }
        token = Token.objects.lookup(
            Token.Type.ACCESS_TOKEN, resp.json()["access_token"]
        )
        refresh_token = Token.objects.lookup(
            Token.Type.REFRESH_TOKEN, resp.json()["refresh_token"]
        )
        assert token.get_grant_id() == refresh_token.get_grant_id()
        assert token.get_grant_id() is not None
        assert set(token.get_resources()) == set(requested_resources)
    else:
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        data = resp.json()
        assert data == {
            "error": "invalid_target",
            "error_description": "The requested resource is invalid, missing, unknown, or malformed.",
        }
