import copy
from unittest.mock import ANY

import pytest


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
                        "code": "enter_current_password",
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
        headless_reverse("headless:account:change_password"),
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


def test_change_password_rate_limit(
    enable_cache,
    auth_client,
    user,
    user_password,
    password_factory,
    settings,
    headless_reverse,
):
    settings.ACCOUNT_RATE_LIMITS = {"change_password": "1/m/ip"}
    for attempt in range(2):
        new_password = password_factory()
        resp = auth_client.post(
            headless_reverse("headless:account:change_password"),
            data={
                "current_password": user_password,
                "new_password": new_password,
            },
            content_type="application/json",
        )
        user_password = new_password
        expected_status = 200 if attempt == 0 else 429
        assert resp.status_code == expected_status
        assert resp.json()["status"] == expected_status
