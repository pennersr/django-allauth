import json

from django.conf import settings
from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects

from allauth.account import app_settings


@pytest.mark.parametrize(
    "headers,ajax_expected",
    [
        ({}, False),
        ({"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}, True),
        ({"HTTP_ACCEPT": "application/json"}, True),
    ],
)
def test_ajax_headers(db, client, headers, ajax_expected):
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": "john@example.org",
            "email2": "john@example.org",
            "password1": "johndoe",
            "password2": "johndoe",
        },
        **headers,
    )
    if ajax_expected:
        assert resp.status_code == 200
        assert resp.json()["location"] == settings.LOGIN_REDIRECT_URL
        assert resp.json()["location"] == settings.LOGIN_REDIRECT_URL
    else:
        assert resp.status_code == 302
        assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )


def test_ajax_password_reset(client, user, mailoutbox):
    resp = client.post(
        reverse("account_reset_password"),
        data={"email": user.email},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [user.email]
    assert resp["content-type"] == "application/json"


def test_ajax_login_fail(client, db):
    resp = client.post(
        reverse("account_login"),
        {},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert resp.status_code == 400
    json.loads(resp.content.decode("utf8"))
    # TODO: Actually test something


def test_ajax_login_success(settings, user, user_password, client):
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.OPTIONAL
    resp = client.post(
        reverse("account_login"),
        {"login": user.username, "password": user_password},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert resp.status_code == 200
    data = json.loads(resp.content.decode("utf8"))
    assert data["location"] == "/accounts/profile/"
