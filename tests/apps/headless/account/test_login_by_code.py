import time
from http import HTTPStatus

from allauth.account.internal.stagekit import LOGIN_SESSION_KEY
from allauth.account.models import EmailAddress
from allauth.account.stages import LoginByCodeStage
from allauth.headless.constants import Flow


def test_login_by_code(headless_reverse, user, client, mailoutbox):
    resp = client.post(
        headless_reverse("headless:account:request_login_code"),
        data={"email": user.email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
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
    assert resp.status_code == HTTPStatus.OK
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
        expected_code = HTTPStatus.BAD_REQUEST if attempt else HTTPStatus.UNAUTHORIZED
        assert resp.status_code == expected_code
        data = resp.json()
        assert data["status"] == expected_code
        if expected_code == HTTPStatus.BAD_REQUEST:
            assert data["errors"] == [
                {
                    "code": "too_many_login_attempts",
                    "message": "Too many failed login attempts. Try again later.",
                    "param": "email",
                },
            ]


def test_login_by_code_max_attemps(headless_reverse, user, client, settings):
    settings.ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS = 2
    resp = client.post(
        headless_reverse("headless:account:request_login_code"),
        data={"email": user.email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    for i in range(3):
        resp = client.post(
            headless_reverse("headless:account:confirm_login_code"),
            data={"code": "wrong"},
            content_type="application/json",
        )
        session_resp = client.get(
            headless_reverse("headless:account:current_session"),
            data={"code": "wrong"},
            content_type="application/json",
        )
        assert session_resp.status_code == HTTPStatus.UNAUTHORIZED
        pending_flows = [
            f for f in session_resp.json()["data"]["flows"] if f.get("is_pending")
        ]
        if i >= 1:
            assert (
                resp.status_code == HTTPStatus.CONFLICT
                if i >= 2
                else HTTPStatus.BAD_REQUEST
            )
            assert len(pending_flows) == 0
        else:
            assert resp.status_code == HTTPStatus.BAD_REQUEST
            assert len(pending_flows) == 1


def test_login_by_code_required(
    client, settings, user_factory, password_factory, headless_reverse, mailoutbox
):
    settings.ACCOUNT_LOGIN_BY_CODE_REQUIRED = True
    password = password_factory()
    user = user_factory(password=password, email_verified=False)
    email_address = EmailAddress.objects.get(email=user.email)
    assert not email_address.verified
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "username": user.username,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    pending_flow = [f for f in resp.json()["data"]["flows"] if f.get("is_pending")][0][
        "id"
    ]
    assert pending_flow == Flow.LOGIN_BY_CODE
    code = [line for line in mailoutbox[0].body.splitlines() if len(line) == 6][0]
    resp = client.post(
        headless_reverse("headless:account:confirm_login_code"),
        data={"code": code},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["meta"]["is_authenticated"]
    email_address.refresh_from_db()
    assert email_address.verified


def test_login_by_code_expired(headless_reverse, user, client, mailoutbox):
    resp = client.post(
        headless_reverse("headless:account:request_login_code"),
        data={"email": user.email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    data = resp.json()
    assert [f for f in data["data"]["flows"] if f["id"] == Flow.LOGIN_BY_CODE][0][
        "is_pending"
    ]
    assert len(mailoutbox) == 1
    code = [line for line in mailoutbox[0].body.splitlines() if len(line) == 6][0]

    # Expire code
    session = client.headless_session()
    login = session[LOGIN_SESSION_KEY]
    login["state"]["stages"][LoginByCodeStage.key]["data"]["at"] = (
        time.time() - 24 * 60 * 60
    )
    session["account_login"] = login
    session.save()

    # Post valid code
    resp = client.post(
        headless_reverse("headless:account:confirm_login_code"),
        data={"code": code},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.CONFLICT


def test_post_login_code_when_flow_not_pending(
    db,
    client,
    settings_impacting_urls,
    headless_reverse,
    mailoutbox,
    get_last_email_verification_code,
):
    with settings_impacting_urls(
        ACCOUNT_LOGIN_METHODS={"email"},
        ACCOUNT_SIGNUP_FIELDS=["email*"],
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        ACCOUNT_LOGIN_BY_CODE_ENABLED=True,
        ACCOUNT_LOGIN_BY_CODE_REQUIRED=False,
        ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True,
    ):
        resp = client.post(
            headless_reverse("headless:account:signup"),
            data={"email": "user@email.org"},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.UNAUTHORIZED
        resp = client.post(
            headless_reverse("headless:account:confirm_login_code"),
            data={"code": "123"},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.CONFLICT
