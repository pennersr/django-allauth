import pytest


def test_password_reset_flow(
    client, user, mailoutbox, password_factory, settings, headless_reverse
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True

    resp = client.post(
        headless_reverse("headless:request_password_reset"),
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
        headless_reverse("headless:reset_password"),
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
        headless_reverse("headless:reset_password"),
        data={
            "key": key,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 200

    user.refresh_from_db()
    assert user.check_password(password)
    assert len(mailoutbox) == 2  # The security notification


@pytest.mark.parametrize("method", ["get", "post"])
def test_password_reset_flow_wrong_key(
    client, password_factory, headless_reverse, method
):
    password = password_factory()

    resp = getattr(client, method)(
        headless_reverse("headless:reset_password"),
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
