from http import HTTPStatus
from unittest.mock import ANY

from django.contrib.auth.models import User

import pytest

from allauth.account import app_settings
from allauth.account.models import EmailAddress
from allauth.headless.constants import Flow


def test_email_verification_rate_limits_login(
    client,
    db,
    user_password,
    settings,
    user_factory,
    password_factory,
    enable_cache,
    headless_reverse,
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_RATE_LIMITS = {"confirm_email": "1/m/key"}
    email = "user@email.org"
    user_factory(email=email, email_verified=False, password=user_password)
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "email": email,
                "password": user_password,
            },
            content_type="application/json",
        )
        if attempt == 0:
            assert resp.status_code == 401
            flow = [
                flow for flow in resp.json()["data"]["flows"] if flow.get("is_pending")
            ][0]
            assert flow["id"] == Flow.VERIFY_EMAIL
        else:
            assert resp.status_code == 400
            assert resp.json() == {
                "status": 400,
                "errors": [
                    {
                        "message": "Too many failed login attempts. Try again later.",
                        "code": "too_many_login_attempts",
                    }
                ],
            }


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_email_verification_rate_limits_submitting_codes(
    client,
    db,
    user_password,
    settings,
    user_factory,
    password_factory,
    enable_cache,
    headless_reverse,
    method,
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_RATE_LIMITS = {"confirm_email": "1/m/key"}
    email = "user@email.org"
    user_factory(email=email, email_verified=False, password=user_password)
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": email,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    flow = [flow for flow in resp.json()["data"]["flows"] if flow.get("is_pending")][0]
    assert flow["id"] == Flow.VERIFY_EMAIL

    for i in range(app_settings.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS):
        if method == "GET":
            resp = client.get(
                headless_reverse("headless:account:verify_email"),
                HTTP_X_EMAIL_VERIFICATION_KEY="123",
            )
        else:
            resp = client.post(
                headless_reverse("headless:account:verify_email"),
                data={
                    "key": "123",
                },
                content_type="application/json",
            )
        if i < app_settings.EMAIL_VERIFICATION_BY_CODE_MAX_ATTEMPTS:
            assert resp.json() == {
                "status": 400,
                "errors": [
                    {
                        "message": "Incorrect code.",
                        "code": "incorrect_code",
                        "param": "key",
                    }
                ],
            }
            assert resp.status_code == 400
        else:
            assert resp.status_code == 409


def test_add_email(
    auth_client,
    user,
    email_factory,
    headless_reverse,
    settings,
    get_last_email_verification_code,
    mailoutbox,
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_CHANGE_EMAIL = True
    new_email = email_factory()

    # Let's add an email...
    resp = auth_client.post(
        headless_reverse("headless:account:manage_email"),
        data={"email": new_email},
        content_type="application/json",
    )
    assert resp.status_code == 200

    # It's in the response, albeit unverified.
    assert len(resp.json()["data"]) == 2
    email_map = {addr["email"]: addr for addr in resp.json()["data"]}
    assert not email_map[new_email]["verified"]

    # Verify the email with an invalid code.
    resp = auth_client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": "key"},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {"message": "Incorrect code.", "code": "incorrect_code", "param": "key"}
        ],
    }

    # And with the valid code...
    code = get_last_email_verification_code(auth_client, mailoutbox)
    resp = auth_client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["user"]["email"] == new_email

    # ACCOUNT_CHANGE_EMAIL = True, so the other one is gone.
    assert EmailAddress.objects.filter(user=user).count() == 1

    # Re-verification won't work...
    resp = auth_client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    assert resp.status_code == 409


@pytest.mark.parametrize("login_on_email_verification", [False, True])
def test_signup_with_email_verification(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
    get_last_email_verification_code,
    login_on_email_verification,
    mailoutbox,
):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_USERNAME_REQUIRED = False
    # This setting should have no affect:
    settings.ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = login_on_email_verification
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    email = email_factory()
    resp = client.post(
        headless_reverse("headless:account:signup"),
        data={
            "email": email,
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    assert User.objects.filter(email=email).exists()
    data = resp.json()
    flow = next((f for f in data["data"]["flows"] if f.get("is_pending")))
    assert flow["id"] == "verify_email"

    code = get_last_email_verification_code(client, mailoutbox)
    resp = client.get(
        headless_reverse("headless:account:verify_email"),
        HTTP_X_EMAIL_VERIFICATION_KEY=code,
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "email": email,
            "user": ANY,
        },
        "meta": {"is_authenticating": True},
        "status": 200,
    }
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    addr = EmailAddress.objects.get(email=email)
    assert addr.verified

    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["is_authenticated"]


@pytest.mark.parametrize("rate_limit_enabled", [(False,), (True,)])
def test_resend_at_signup(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
    get_last_email_verification_code,
    mailoutbox,
    rate_limit_enabled,
    request,
):
    if rate_limit_enabled:
        request.getfixturevalue("enable_cache")
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_USERNAME_REQUIRED = False
    # This setting should have no affect:
    settings.ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_RESEND = True
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    email = email_factory()
    resp = client.post(
        headless_reverse("headless:account:signup"),
        data={
            "email": email,
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    assert User.objects.filter(email=email).exists()
    data = resp.json()
    flow = next((f for f in data["data"]["flows"] if f.get("is_pending")))
    assert flow["id"] == "verify_email"

    code = get_last_email_verification_code(client, mailoutbox)
    resp = client.get(
        headless_reverse("headless:account:verify_email"),
        HTTP_X_EMAIL_VERIFICATION_KEY=code,
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "email": email,
            "user": ANY,
        },
        "meta": {"is_authenticating": True},
        "status": HTTPStatus.OK,
    }
    resp = client.post(
        headless_reverse("headless:account:resend_email_verification_code"),
    )
    if rate_limit_enabled:
        assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS
    else:
        assert resp.status_code == HTTPStatus.OK

        new_code = get_last_email_verification_code(client, mailoutbox)
        assert code != new_code
