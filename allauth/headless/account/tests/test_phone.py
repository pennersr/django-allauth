from http import HTTPStatus


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
