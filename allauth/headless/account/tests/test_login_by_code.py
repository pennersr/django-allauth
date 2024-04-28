from allauth.headless.constants import Flow


def test_login_by_code(headless_reverse, user, client, mailoutbox):
    resp = client.post(
        headless_reverse("headless:account:request_login_code"),
        data={"email": user.email},
        content_type="application/json",
    )
    assert resp.status_code == 401
    data = resp.json()
    assert [f for f in data["data"]["flows"] if f["id"] == Flow.LOGIN_BY_CODE][0][
        "is_pending"
    ]
    assert len(mailoutbox) == 1
    code = [line for line in mailoutbox[0].body.splitlines() if len(line) == 6][0]
    resp = client.post(
        headless_reverse("headless:account:confirm_login_code"),
        data={"code": code},
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["is_authenticated"]


def test_login_by_code_rate_limit(
    headless_reverse, user, client, mailoutbox, settings, enable_cache
):
    settings.ACCOUNT_RATE_LIMITS = {"request_login_code": "1/m/ip"}
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:request_login_code"),
            data={"email": user.email},
            content_type="application/json",
        )
        expected_code = 400 if attempt else 401
        assert resp.status_code == expected_code
        data = resp.json()
        assert data["status"] == expected_code
        if expected_code == 400:
            assert data["errors"] == [
                {
                    "code": "too_many_login_attempts",
                    "message": "Too many failed login attempts. Try again later.",
                    "param": "email",
                },
            ]
