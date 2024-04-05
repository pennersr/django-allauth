from unittest.mock import ANY

import pytest


def test_auth_password_input_error(headless_reverse, client):
    resp = client.post(
        headless_reverse("headless:login"),
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
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    resp = client.post(
        headless_reverse("headless:login"),
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
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    login_resp = client.post(
        headless_reverse("headless:login"),
        data={
            "email": user.email,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert login_resp.status_code == 200
    session_resp = client.get(
        headless_reverse("headless:current_session"),
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
        headless_reverse("headless:login"),
        data={
            "username": user.username,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == status_code
