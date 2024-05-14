from django.urls import reverse

import pytest


def test_password_reset_flow(
    client, user, mailoutbox, password_factory, settings, headless_reverse
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True

    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": user.email,
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert len(mailoutbox) == 1
    body = mailoutbox[0].body
    # Extract URL for `password_reset_from_key` view
    url = body[body.find("/password/reset/") :].split()[0]
    key = url.split("/")[-2]
    password = password_factory()

    # Too simple password
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        data={
            "key": key,
            "password": "a",
        },
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {
                "code": "password_too_short",
                "message": "This password is too short. It must contain at least 6 characters.",
            }
        ],
    }

    assert len(mailoutbox) == 1

    # Success
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        data={
            "key": key,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401

    user.refresh_from_db()
    assert user.check_password(password)
    assert len(mailoutbox) == 2  # The security notification


@pytest.mark.parametrize("method", ["get", "post"])
def test_password_reset_flow_wrong_key(
    client, password_factory, headless_reverse, method
):
    password = password_factory()

    if method == "get":
        resp = client.get(
            headless_reverse("headless:account:reset_password"),
            HTTP_X_PASSWORD_RESET_KEY="wrong",
        )
    else:
        resp = client.post(
            headless_reverse("headless:account:reset_password"),
            data={
                "key": "wrong",
                "password": password,
            },
            content_type="application/json",
        )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {
                "param": "key",
                "code": "invalid_password_reset",
                "message": "The password reset token was invalid.",
            }
        ],
    }


def test_password_reset_flow_unknown_user(
    client, db, mailoutbox, password_factory, settings, headless_reverse
):
    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": "not@registered.org",
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert len(mailoutbox) == 1
    body = mailoutbox[0].body
    if getattr(settings, "HEADLESS_ONLY", False):
        assert settings.HEADLESS_FRONTEND_URLS["account_signup"] in body
    else:
        assert reverse("account_signup") in body


def test_reset_password_rate_limit(
    auth_client, user, headless_reverse, settings, enable_cache
):
    settings.ACCOUNT_RATE_LIMITS = {"reset_password": "1/m/ip"}
    for attempt in range(2):
        resp = auth_client.post(
            headless_reverse("headless:account:request_password_reset"),
            data={"email": user.email},
            content_type="application/json",
        )
        expected_status = 200 if attempt == 0 else 429
        assert resp.status_code == expected_status
        assert resp.json()["status"] == expected_status


def test_password_reset_key_rate_limit(
    client,
    user,
    settings,
    headless_reverse,
    password_reset_key_generator,
    enable_cache,
):
    settings.ACCOUNT_RATE_LIMITS = {"reset_password_from_key": "1/m/ip"}
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:reset_password"),
            data={
                "key": password_reset_key_generator(user),
                "password": "a",  # too short
            },
            content_type="application/json",
        )
        expected_status = 429 if attempt else 400
        assert resp.status_code == expected_status
        assert resp.json()["status"] == expected_status
