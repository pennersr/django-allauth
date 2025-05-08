from http import HTTPStatus

from django.contrib.auth import get_user_model

import pytest

from allauth.account.adapter import get_adapter as get_account_adapter


def test_change_phone_to_same(
    auth_client, user_with_phone, phone, settings_impacting_urls, headless_reverse
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        resp = auth_client.post(
            headless_reverse("headless:account:manage_phone"),
            data={
                "phone": phone,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "errors": [
                {
                    "code": "same_as_current",
                    "message": "The new value must be different from the current one.",
                    "param": "phone",
                }
            ],
            "status": HTTPStatus.BAD_REQUEST,
        }


def test_change_phone(
    auth_client,
    user_with_phone,
    phone,
    settings_impacting_urls,
    headless_reverse,
    phone_factory,
    sms_outbox,
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        new_phone = phone_factory()
        resp = auth_client.post(
            headless_reverse("headless:account:manage_phone"),
            data={
                "phone": new_phone,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.ACCEPTED
        assert resp.json() == {
            "data": [
                {
                    "phone": new_phone,
                    "verified": False,
                },
            ],
            "status": HTTPStatus.ACCEPTED,
        }

        resp = auth_client.post(
            headless_reverse("headless:account:verify_phone"),
            data={
                "code": sms_outbox[-1]["code"],
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK

        resp = auth_client.post(
            headless_reverse("headless:account:verify_phone"),
            data={
                "code": sms_outbox[-1]["code"],
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.CONFLICT

        resp = auth_client.get(
            headless_reverse("headless:account:manage_phone"),
            content_type="application/json",
        )
        assert resp.json() == {
            "data": [
                {
                    "phone": new_phone,
                    "verified": True,
                },
            ],
            "status": 200,
        }


def test_login(
    client,
    user_with_phone,
    phone,
    user_password,
    headless_reverse,
    settings_impacting_urls,
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={"phone": phone, "password": user_password},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK


def test_login_by_code(
    client,
    user_with_phone,
    phone,
    headless_reverse,
    settings_impacting_urls,
    sms_outbox,
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        resp = client.post(
            headless_reverse("headless:account:request_login_code"),
            data={
                "phone": phone,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        code = sms_outbox[-1]["code"]
        resp = client.post(
            headless_reverse("headless:account:confirm_login_code"),
            data={"code": code},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK
        data = resp.json()
        assert data["meta"]["is_authenticated"]


def test_signup(
    db,
    client,
    settings_impacting_urls,
    phone,
    headless_reverse,
    headless_client,
    password_factory,
    sms_outbox,
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        resp = client.post(
            headless_reverse("headless:account:signup"),
            data={
                "phone": phone,
                "password": password_factory(),
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        pending_flow = [
            flow for flow in resp.json()["data"]["flows"] if flow.get("is_pending")
        ][0]
        assert pending_flow["id"] == "verify_phone"
        assert len(sms_outbox) == 1
        code = sms_outbox[-1]["code"]
        resp = client.post(
            headless_reverse("headless:account:verify_phone"),
            data={
                "code": code,
            },
            content_type="application/json",
        )
        assert resp.json()["status"] == HTTPStatus.OK


def test_reauthentication(
    auth_client,
    user_with_phone,
    phone,
    settings_impacting_urls,
    headless_reverse,
    phone_factory,
    sms_outbox,
):
    with settings_impacting_urls(
        ACCOUNT_REAUTHENTICATION_REQUIRED=True,
        ACCOUNT_SIGNUP_FIELDS=["phone*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        new_phone = phone_factory()
        resp = auth_client.post(
            headless_reverse("headless:account:manage_phone"),
            data={
                "phone": new_phone,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert resp.json()["data"]["flows"] == [{"id": "reauthenticate"}]


def test_change_phone_to_conflicting(
    auth_client,
    user_with_phone,
    phone,
    settings_impacting_urls,
    headless_reverse,
    user_factory,
    phone_factory,
    sms_outbox,
):
    other_phone = phone_factory()
    user_factory(phone=other_phone)
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
    ):
        resp = auth_client.post(
            headless_reverse("headless:account:manage_phone"),
            data={
                "phone": other_phone,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.ACCEPTED
        assert resp.json() == {
            "data": [{"phone": other_phone, "verified": False}],
            "status": HTTPStatus.ACCEPTED,
        }
        resp = auth_client.post(
            headless_reverse("headless:account:verify_phone"),
            data={
                "code": sms_outbox[-1]["code"],
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.json() == {
            "errors": [
                {
                    "code": "phone_taken",
                    "message": "A user is already registered with this phone number.",
                    "param": "code",
                }
            ],
            "status": HTTPStatus.BAD_REQUEST,
        }


def test_change_at_signup(
    db,
    client,
    settings_impacting_urls,
    phone,
    headless_reverse,
    headless_client,
    password_factory,
    sms_outbox,
    phone_factory,
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
        ACCOUNT_PHONE_VERIFICATION_SUPPORTS_CHANGE=True,
    ):
        resp = client.post(
            headless_reverse("headless:account:signup"),
            data={
                "phone": phone,
                "password": password_factory(),
            },
            content_type="application/json",
        )
        user = get_user_model().objects.last()
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert len(sms_outbox) == 1

        new_phone = phone_factory()
        resp = client.post(
            headless_reverse("headless:account:manage_phone"),
            data={
                "phone": new_phone,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.ACCEPTED
        assert resp.json() == {
            "data": [
                {
                    "phone": new_phone,
                    "verified": False,
                },
            ],
            "status": HTTPStatus.ACCEPTED,
        }

        assert len(sms_outbox) == 2
        code = sms_outbox[-1]["code"]
        resp = client.post(
            headless_reverse("headless:account:verify_phone"),
            data={
                "code": code,
            },
            content_type="application/json",
        )
        assert resp.json()["status"] == HTTPStatus.OK
        assert get_account_adapter().get_phone(user) == (new_phone, True)


@pytest.mark.parametrize("rate_limit_enabled", [(False,), (True,)])
def test_resend_at_signup(
    db,
    client,
    settings_impacting_urls,
    phone,
    headless_reverse,
    headless_client,
    password_factory,
    sms_outbox,
    phone_factory,
    rate_limit_enabled,
    request,
):
    if rate_limit_enabled:
        request.getfixturevalue("enable_cache")
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
        ACCOUNT_LOGIN_METHODS=("phone",),
        ACCOUNT_PHONE_VERIFICATION_SUPPORTS_RESEND=True,
    ):
        resp = client.post(
            headless_reverse("headless:account:signup"),
            data={
                "phone": phone,
                "password": password_factory(),
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        assert len(sms_outbox) == 1

        resp = client.post(
            headless_reverse("headless:account:resend_phone_verification_code"),
        )
        if rate_limit_enabled:
            assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS
        else:
            assert resp.status_code == HTTPStatus.OK
            assert len(sms_outbox) == 2

            old_code = sms_outbox[0]["code"]
            new_code = sms_outbox[1]["code"]
            assert old_code != new_code
