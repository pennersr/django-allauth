from http import HTTPStatus

import pytest

from allauth.account import app_settings
from allauth.account.models import EmailAddress


@pytest.fixture(autouse=True)
def prbc_settings(settings_impacting_urls):
    with settings_impacting_urls(ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED=True):
        yield


def test_validating_codes_by_get_is_limited(client, user, headless_reverse):
    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": user.email,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    for i in range(app_settings.PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS + 1):
        resp = client.get(
            headless_reverse("headless:account:reset_password"),
            HTTP_X_PASSWORD_RESET_KEY=f"attempt{i}",
        )
        if i < app_settings.PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS:
            expected_status = HTTPStatus.BAD_REQUEST
        else:
            expected_status = HTTPStatus.CONFLICT
        assert resp.status_code == expected_status


def test_validating_codes_by_get_limitation_carriers_over_to_post(
    client, user, headless_reverse
):
    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": user.email,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    for i in range(app_settings.PASSWORD_RESET_BY_CODE_MAX_ATTEMPTS):
        resp = client.get(
            headless_reverse("headless:account:reset_password"),
            HTTP_X_PASSWORD_RESET_KEY=f"attempt{i}",
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        data={
            "key": "wrong",
            "password": "a",
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.CONFLICT


def test_password_reset_flow(
    client,
    user,
    mailoutbox,
    password_factory,
    settings,
    headless_reverse,
    get_last_password_reset_code,
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True

    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": user.email,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    code = get_last_password_reset_code(client, mailoutbox)
    password = password_factory()

    # Get token info
    resp = client.get(
        headless_reverse("headless:account:reset_password"),
        content_type="application/json",
        HTTP_X_PASSWORD_RESET_KEY=code,
    )
    assert resp.status_code == HTTPStatus.OK

    # Too simple password
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        data={
            "key": code,
            "password": "a",
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [
            {
                "code": "password_too_short",
                "message": "This password is too short. It must contain at least 6 characters.",
                "param": "password",
            }
        ],
    }

    assert len(mailoutbox) == 1

    # Success
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        data={
            "key": code,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    user.refresh_from_db()
    assert user.check_password(password)
    assert len(mailoutbox) == 2  # The security notification

    # Try once more, shouldn't be allowed.
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        data={
            "key": code,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.CONFLICT


def test_indirect_email_verification_on_get(
    db, client, mailoutbox, get_last_password_reset_code, user_factory, headless_reverse
):
    user = user_factory(email_verified=False)
    address = EmailAddress.objects.get(user=user, email=user.email, verified=False)
    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": address.email,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    resp = client.get(
        headless_reverse("headless:account:reset_password"),
        HTTP_X_PASSWORD_RESET_KEY=get_last_password_reset_code(client, mailoutbox),
    )
    assert resp.status_code == HTTPStatus.OK
    address.refresh_from_db()
    assert address.verified


def test_indirect_email_verification_on_post(
    db,
    client,
    mailoutbox,
    get_last_password_reset_code,
    user_factory,
    headless_reverse,
    password_factory,
):
    user = user_factory(email_verified=False)
    address = EmailAddress.objects.get(user=user, email=user.email, verified=False)
    resp = client.post(
        headless_reverse("headless:account:request_password_reset"),
        data={
            "email": address.email,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    resp = client.post(
        headless_reverse("headless:account:reset_password"),
        {
            "key": get_last_password_reset_code(client, mailoutbox),
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    address.refresh_from_db()
    assert address.verified
