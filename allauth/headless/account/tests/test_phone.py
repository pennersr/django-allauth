from http import HTTPStatus


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
            "status": 202,
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
