from unittest.mock import ANY

from django.contrib.auth import get_user_model

import pytest

from allauth.account import app_settings
from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.headless.constants import Flow
from allauth.mfa.models import Authenticator


def test_passkey_login(
    client, passkey, webauthn_authentication_bypass, headless_reverse
):
    with webauthn_authentication_bypass(passkey) as credential:
        resp = client.get(headless_reverse("headless:mfa:login_webauthn"))
        assert "request_options" in resp.json()["data"]
        resp = client.post(
            headless_reverse("headless:mfa:login_webauthn"),
            data={"credential": credential},
            content_type="application/json",
        )
    data = resp.json()
    assert data["data"]["user"]["id"] == passkey.user_id


def test_passkey_login_get_options(client, headless_client, headless_reverse, db):
    resp = client.get(headless_reverse("headless:mfa:login_webauthn"))
    data = resp.json()
    meta = {}
    if headless_client == "app":
        meta = {
            "meta": {"session_token": ANY},
        }
    assert data == {
        "status": 200,
        "data": {"request_options": {"publicKey": ANY}},
        **meta,
    }


def test_reauthenticate(
    auth_client,
    passkey,
    user_with_recovery_codes,
    webauthn_authentication_bypass,
    headless_reverse,
):
    # View recovery codes, confirm webauthn reauthentication is an option
    resp = auth_client.get(headless_reverse("headless:mfa:manage_recovery_codes"))
    assert resp.status_code == 401
    assert Flow.MFA_REAUTHENTICATE in [
        flow["id"] for flow in resp.json()["data"]["flows"]
    ]

    # Get request options
    with webauthn_authentication_bypass(passkey):
        resp = auth_client.get(headless_reverse("headless:mfa:reauthenticate_webauthn"))
        data = resp.json()
        assert data["status"] == 200
        assert data["data"]["request_options"] == ANY

    # Reauthenticate
    with webauthn_authentication_bypass(passkey) as credential:
        resp = auth_client.post(
            headless_reverse("headless:mfa:reauthenticate_webauthn"),
            data={"credential": credential},
            content_type="application/json",
        )
        assert resp.status_code == 200
    resp = auth_client.get(headless_reverse("headless:mfa:manage_recovery_codes"))
    assert resp.status_code == 200


def test_update_authenticator(
    auth_client, headless_reverse, passkey, reauthentication_bypass
):
    data = {"id": passkey.pk, "name": "Renamed!"}
    resp = auth_client.put(
        headless_reverse("headless:mfa:manage_webauthn"),
        data=data,
        content_type="application/json",
    )
    # Reauthentication required
    assert resp.status_code == 401
    with reauthentication_bypass():
        resp = auth_client.put(
            headless_reverse("headless:mfa:manage_webauthn"),
            data=data,
            content_type="application/json",
        )
    assert resp.status_code == 200
    passkey.refresh_from_db()
    assert passkey.wrap().name == "Renamed!"


def test_delete_authenticator(
    auth_client, headless_reverse, passkey, reauthentication_bypass
):
    data = {"authenticators": [passkey.pk]}
    resp = auth_client.delete(
        headless_reverse("headless:mfa:manage_webauthn"),
        data=data,
        content_type="application/json",
    )
    # Reauthentication required
    assert resp.status_code == 401
    with reauthentication_bypass():
        resp = auth_client.delete(
            headless_reverse("headless:mfa:manage_webauthn"),
            data=data,
            content_type="application/json",
        )
    assert resp.status_code == 200
    assert not Authenticator.objects.filter(pk=passkey.pk).exists()


@pytest.mark.parametrize("email_verified", [False, True])
def test_add_authenticator(
    user,
    auth_client,
    headless_reverse,
    webauthn_registration_bypass,
    reauthentication_bypass,
    email_verified,
):
    resp = auth_client.get(headless_reverse("headless:mfa:manage_webauthn"))
    # Reauthentication required
    assert resp.status_code == 401 if email_verified else 409

    with reauthentication_bypass():
        resp = auth_client.get(headless_reverse("headless:mfa:manage_webauthn"))
        if email_verified:
            assert resp.status_code == 200
            data = resp.json()
            assert data["data"]["creation_options"] == ANY
        else:
            assert resp.status_code == 409

        with webauthn_registration_bypass(user, False) as credential:
            resp = auth_client.post(
                headless_reverse("headless:mfa:manage_webauthn"),
                data={"credential": credential},
                content_type="application/json",
            )
            webauthn_count = Authenticator.objects.filter(
                type=Authenticator.Type.WEBAUTHN, user=user
            ).count()
            if email_verified:
                assert resp.status_code == 200
                assert webauthn_count == 1
            else:
                assert resp.status_code == 409
                assert webauthn_count == 0


def test_2fa_login(
    client,
    user,
    user_password,
    passkey,
    webauthn_authentication_bypass,
    headless_reverse,
):
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "username": user.username,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    data = resp.json()
    pending_flows = [f for f in data["data"]["flows"] if f.get("is_pending")]
    assert len(pending_flows) == 1
    pending_flow = pending_flows[0]
    assert pending_flow == {
        "id": "mfa_authenticate",
        "is_pending": True,
        "types": ["webauthn"],
    }
    with webauthn_authentication_bypass(passkey) as credential:
        resp = client.get(headless_reverse("headless:mfa:authenticate_webauthn"))
        assert "request_options" in resp.json()["data"]
        resp = client.post(
            headless_reverse("headless:mfa:authenticate_webauthn"),
            data={"credential": credential},
            content_type="application/json",
        )
    data = resp.json()
    assert resp.status_code == 200
    assert data["data"]["user"]["id"] == passkey.user_id
    assert client.headless_session()[AUTHENTICATION_METHODS_SESSION_KEY] == [
        {"method": "password", "at": ANY, "username": passkey.user.username},
        {"method": "mfa", "at": ANY, "id": ANY, "type": Authenticator.Type.WEBAUTHN},
    ]


@pytest.mark.parametrize("login_on_email_verification", [False, True])
def test_passkey_signup(
    client,
    db,
    webauthn_registration_bypass,
    headless_reverse,
    settings,
    get_last_email_verification_code,
    mailoutbox,
    login_on_email_verification,
):
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.MANDATORY
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    # This setting should have no influence when verifying by code:
    settings.ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = login_on_email_verification

    # Initiate passkey signup
    resp = client.post(
        headless_reverse("headless:mfa:signup_webauthn"),
        data={"email": "pass@key.org", "username": "passkey"},
        content_type="application/json",
    )

    # Email verification kicks in.
    assert resp.status_code == 401
    pending_flows = [
        flow for flow in resp.json()["data"]["flows"] if flow.get("is_pending")
    ]
    assert len(pending_flows) == 1
    flow = pending_flows[0]
    assert flow["id"] == Flow.VERIFY_EMAIL.value

    # Verify email.
    code = get_last_email_verification_code(client, mailoutbox)
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    assert resp.status_code == 401

    # Now, the webauthn signup flow is pending.
    pending_flows = [
        flow for flow in resp.json()["data"]["flows"] if flow.get("is_pending")
    ]
    assert len(pending_flows) == 1
    flow = pending_flows[0]
    assert flow["id"] == Flow.MFA_SIGNUP_WEBAUTHN.value

    # Fetch flow creation options.
    resp = client.get(headless_reverse("headless:mfa:signup_webauthn"))
    data = resp.json()
    assert "creation_options" in data["data"]

    # Create a passkey.
    user = get_user_model().objects.get(email="pass@key.org")
    with webauthn_registration_bypass(user, True) as credential:
        resp = client.put(
            headless_reverse("headless:mfa:signup_webauthn"),
            data={"name": "Some key", "credential": credential},
            content_type="application/json",
        )

    # Signed up successfully.
    data = resp.json()
    assert resp.status_code == 200
    assert data["meta"]["is_authenticated"]
    authenticator = Authenticator.objects.get(user=user)
    assert authenticator.wrap().name == "Some key"
