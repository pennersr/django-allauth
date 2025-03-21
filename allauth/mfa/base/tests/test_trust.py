import time
from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

import pytest

from allauth.mfa import app_settings
from allauth.mfa.internal.flows import trust


def test_encode_decode(rf):
    request = rf.get("/")
    value = trust.encode_trust_cookie(
        [
            trust.IssuedTrust(fingerprint="dated", at=2024),
            trust.IssuedTrust(fingerprint="good", at=time.time()),
        ]
    )
    request.COOKIES[app_settings.TRUST_COOKIE_NAME] = value
    trusts = trust.decode_trust_cookie(request)
    assert len(trusts) == 1
    assert trusts[0].fingerprint == "good"


def test_decode_invalid_value(rf):
    request = rf.get("/")
    request.COOKIES[app_settings.TRUST_COOKIE_NAME] = "bad"
    trusts = trust.decode_trust_cookie(request)
    assert len(trusts) == 0


@pytest.mark.parametrize("action", ["", "trust"])
def test_trust_flow(
    client,
    user_with_totp,
    user_password,
    totp_validation_bypass,
    settings_impacting_urls,
    action,
):
    with settings_impacting_urls(MFA_TRUST_ENABLED=True):
        # Login
        resp = client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        assert resp.status_code == HTTPStatus.FOUND

        # Complete TOTP
        assert resp["location"] == reverse("mfa_authenticate")
        with totp_validation_bypass():
            resp = client.post(
                reverse("mfa_authenticate"),
                {"code": "123"},
            )
        assert resp.status_code == HTTPStatus.FOUND

        # Indicate trust
        assert resp["location"] == reverse("mfa_trust")
        resp = client.post(
            reverse("mfa_trust"),
            {"action": action},
        )
        assert resp["location"] == settings.LOGIN_REDIRECT_URL

        # Sign out
        resp = client.post(
            reverse("account_logout"),
        )
        assert resp.status_code == HTTPStatus.FOUND

        # Sign in
        resp = client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == (
            settings.LOGIN_REDIRECT_URL
            if action == "trust"
            else reverse("mfa_authenticate")
        )
