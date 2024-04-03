import copy
from unittest.mock import ANY

import pytest

from allauth.account.models import EmailAddress, get_emailconfirmation_model


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
    resp = client.post(
        headless_reverse("headless:login"),
        data={
            "email": user.email,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    resp = client.get(
        headless_reverse("headless:current_session"),
        content_type="application/json",
    )
    assert resp.status_code == 200
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
        "meta": {"is_authenticated": True},
    }


def test_auth_unverified_email(
    client, user_factory, password_factory, settings, headless_reverse
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    password = password_factory()
    user = user_factory(email_verified=False, password=password)
    resp = client.post(
        headless_reverse("headless:login"),
        data={
            "email": user.email,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    # FIXME
    # assert resp.json() == {}
    emailaddress = EmailAddress.objects.filter(user=user, verified=False).get()
    key = get_emailconfirmation_model().create(emailaddress).key
    resp = client.post(
        headless_reverse("headless:verify_email"),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == 200


def test_verify_email_bad_key(
    client, settings, password_factory, user_factory, headless_reverse
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    password = password_factory()
    user = user_factory(email_verified=False, password=password)
    resp = client.post(
        headless_reverse("headless:login"),
        data={
            "email": user.email,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    resp = client.post(
        headless_reverse("headless:verify_email"),
        data={"key": "bad"},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {"code": "invalid", "param": "key", "message": "Invalid or expired key."}
        ],
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


def test_password_reset_flow_wrong_key(client, password_factory, headless_reverse):
    password = password_factory()
    resp = client.post(
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
                "code": "",
                "message": "The password reset token was invalid.",
            }
        ],
    }


@pytest.mark.parametrize(
    "has_password,request_data,response_data,status_code",
    [
        # Wrong current password
        (
            True,
            {"current_password": "wrong", "new_password": "{password_factory}"},
            {
                "status": 400,
                "errors": [
                    {
                        "param": "current_password",
                        "message": "Please type your current password.",
                        "code": "",
                    }
                ],
            },
            400,
        ),
        # Happy flow, regular password change
        (
            True,
            {
                "current_password": "{user_password}",
                "new_password": "{password_factory}",
            },
            {
                "status": 200,
                "meta": {"is_authenticated": True},
                "data": {
                    "user": ANY,
                    "methods": [],
                },
            },
            200,
        ),
        # New password does not match constraints
        (
            True,
            {
                "current_password": "{user_password}",
                "new_password": "a",
            },
            {
                "status": 400,
                "errors": [
                    {
                        "param": "new_password",
                        "code": "password_too_short",
                        "message": "This password is too short. It must contain at least 6 characters.",
                    }
                ],
            },
            400,
        ),
        # New password not empty
        (
            True,
            {
                "current_password": "{user_password}",
                "new_password": "",
            },
            {
                "status": 400,
                "errors": [
                    {
                        "param": "new_password",
                        "code": "required",
                        "message": "This field is required.",
                    }
                ],
            },
            400,
        ),
        # Current password not blank
        (
            True,
            {
                "current_password": "",
                "new_password": "{password_factory}",
            },
            {
                "status": 400,
                "errors": [
                    {
                        "param": "current_password",
                        "message": "This field is required.",
                        "code": "required",
                    }
                ],
            },
            400,
        ),
        # Current password missing
        (
            True,
            {
                "new_password": "{password_factory}",
            },
            {
                "status": 400,
                "errors": [
                    {
                        "param": "current_password",
                        "message": "This field is required.",
                        "code": "required",
                    }
                ],
            },
            400,
        ),
        # Current password not set, happy flow
        (
            False,
            {
                "current_password": "",
                "new_password": "{password_factory}",
            },
            {
                "status": 200,
                "meta": {"is_authenticated": True},
                "data": {
                    "user": ANY,
                    "methods": [],
                },
            },
            200,
        ),
        # Current password not set, current_password absent
        (
            False,
            {
                "new_password": "{password_factory}",
            },
            {
                "status": 200,
                "meta": {"is_authenticated": True},
                "data": {
                    "user": ANY,
                    "methods": [],
                },
            },
            200,
        ),
    ],
)
def test_change_password(
    auth_client,
    user,
    request_data,
    response_data,
    status_code,
    has_password,
    user_password,
    password_factory,
    settings,
    mailoutbox,
    headless_reverse,
    headless_client,
):
    request_data = copy.deepcopy(request_data)
    response_data = copy.deepcopy(response_data)
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    if not has_password:
        user.set_unusable_password()
        user.save(update_fields=["password"])
        auth_client.force_login(user)
    if request_data.get("current_password") == "{user_password}":
        request_data["current_password"] = user_password
    if request_data.get("new_password") == "{password_factory}":
        request_data["new_password"] = password_factory()
    resp = auth_client.post(
        headless_reverse("headless:change_password"),
        data=request_data,
        content_type="application/json",
    )
    assert resp.status_code == status_code
    resp_json = resp.json()
    if headless_client == "app" and resp.status_code == 200:
        response_data["meta"]["session_token"] = ANY
    assert resp_json == response_data
    user.refresh_from_db()
    if resp.status_code == 200:
        assert user.check_password(request_data["new_password"])
        assert len(mailoutbox) == 1
    else:
        assert user.check_password(user_password)
        assert len(mailoutbox) == 0
