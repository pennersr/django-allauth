from unittest.mock import ANY

import pytest

from allauth.account.signals import user_logged_in
from allauth.headless.base.response import AuthenticationResponse


def test_auth_password_input_error(headless_reverse, client):
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {
                "message": "This field is required.",
                "code": "required",
                "param": "password",
            },
            {
                "message": "This field is required.",
                "code": "required",
                "param": "username",
            },
        ],
    }


def test_auth_password_bad_password(headless_reverse, client, user, settings):
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": "wrong",
        },
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {
                "param": "password",
                "message": "The email address and/or password you specified are not correct.",
                "code": "email_password_mismatch",
            }
        ],
    }


def test_auth_password_success(
    client, user, user_password, settings, headless_reverse, headless_client
):
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    login_resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert login_resp.status_code == 200
    session_resp = client.get(
        headless_reverse("headless:account:current_session"),
        content_type="application/json",
    )
    assert session_resp.status_code == 200
    for resp in [login_resp, session_resp]:
        extra_meta = {}
        if headless_client == "app" and resp == login_resp:
            # The session is created on first login, and hence the token is
            # exposed only at that moment.
            extra_meta["session_token"] = ANY
        assert resp.json() == {
            "status": 200,
            "data": {
                "user": {
                    "id": user.pk,
                    "display": str(user),
                    "email": user.email,
                    "username": user.username,
                    "has_usable_password": True,
                },
                "methods": [
                    {
                        "at": ANY,
                        "email": user.email,
                        "method": "password",
                    }
                ],
            },
            "meta": {"is_authenticated": True, **extra_meta},
        }


@pytest.mark.parametrize("is_active,status_code", [(False, 401), (True, 200)])
def test_auth_password_user_inactive(
    client, user, user_password, settings, status_code, is_active, headless_reverse
):
    user.is_active = is_active
    user.save(update_fields=["is_active"])
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "username": user.username,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == status_code


def test_login_failed_rate_limit(
    client,
    user,
    settings,
    headless_reverse,
    headless_client,
    enable_cache,
):
    settings.ACCOUNT_RATE_LIMITS = {"login_failed": "1/m/ip"}
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "email": user.email,
                "password": "wrong",
            },
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert resp.json()["errors"] == [
            (
                {
                    "code": "email_password_mismatch",
                    "message": "The email address and/or password you specified are not correct.",
                    "param": "password",
                }
                if attempt == 0
                else {
                    "message": "Too many failed login attempts. Try again later.",
                    "code": "too_many_login_attempts",
                }
            )
        ]


def test_login_rate_limit(
    client,
    user,
    user_password,
    settings,
    headless_reverse,
    headless_client,
    enable_cache,
):
    settings.ACCOUNT_RATE_LIMITS = {"login": "1/m/ip"}
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "email": user.email,
                "password": user_password,
            },
            content_type="application/json",
        )
        expected_status = 429 if attempt else 200
        assert resp.status_code == expected_status


def test_login_already_logged_in(
    auth_client, user, user_password, settings, headless_reverse
):
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    resp = auth_client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 409


def test_custom_post_login_response(
    settings, client, headless_reverse, user, user_password
):
    settings.ACCOUNT_LOGIN_METHODS = {"email"}

    def on_user_logged_in(**kwargs):
        response = kwargs["response"]
        assert isinstance(response, AuthenticationResponse)

    user_logged_in.connect(on_user_logged_in)
    try:
        login_resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "email": user.email,
                "password": user_password,
            },
            content_type="application/json",
        )
        assert login_resp.status_code == 200
    finally:
        user_logged_in.disconnect(on_user_logged_in)
