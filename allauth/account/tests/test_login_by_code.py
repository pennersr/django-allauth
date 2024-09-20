from unittest.mock import ANY

from django.urls import reverse

import pytest

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.account.internal.flows.login_by_code import LOGIN_CODE_STATE_KEY
from allauth.account.internal.stagekit import LOGIN_SESSION_KEY
from allauth.account.models import EmailAddress


@pytest.fixture
def request_login_by_code(mailoutbox):
    def f(client, email):
        resp = client.get(reverse("account_request_login_code") + "?next=/foo")
        assert resp.status_code == 200
        assert b'value="/foo"' in resp.content
        resp = client.post(
            reverse("account_request_login_code"), data={"email": email, "next": "/foo"}
        )
        assert resp.status_code == 302
        assert (
            resp["location"] == reverse("account_confirm_login_code") + "?next=%2Ffoo"
        )
        assert len(mailoutbox) == 1
        code = client.session[LOGIN_SESSION_KEY]["state"][LOGIN_CODE_STATE_KEY]["code"]
        assert len(code) == 6
        assert code in mailoutbox[0].body
        return code

    return f


def test_login_by_code(client, user, request_login_by_code):
    code = request_login_by_code(client, user.email)
    code_with_ws = " " + code[0:3] + " " + code[3:]
    resp = client.post(
        reverse("account_confirm_login_code"),
        data={"code": code_with_ws, "next": "/foo"},
    )
    assert resp.status_code == 302
    assert LOGIN_SESSION_KEY not in client.session
    assert resp["location"] == "/foo"
    assert client.session[AUTHENTICATION_METHODS_SESSION_KEY][-1] == {
        "method": "code",
        "email": user.email,
        "at": ANY,
    }


def test_login_by_code_max_attempts(client, user, request_login_by_code, settings):
    settings.ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS = 2
    request_login_by_code(client, user.email)
    for i in range(3):
        resp = client.post(
            reverse("account_confirm_login_code"), data={"code": "wrong"}
        )
        if i >= 1:
            assert resp.status_code == 302
            assert resp["location"] == reverse("account_request_login_code")
            assert LOGIN_SESSION_KEY not in client.session
        else:
            assert resp.status_code == 200
            assert LOGIN_SESSION_KEY in client.session
            assert resp.context["form"].errors == {"code": ["Incorrect code."]}


def test_login_by_code_unknown_user(mailoutbox, client, db):
    resp = client.post(
        reverse("account_request_login_code"),
        data={"email": "unknown@email.org"},
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_confirm_login_code")
    resp = client.post(reverse("account_confirm_login_code"), data={"code": "123456"})


@pytest.mark.parametrize(
    "setting,code_required",
    [
        (True, True),
        ({"password"}, True),
        ({"socialaccount"}, False),
    ],
)
def test_login_by_code_required(
    client, settings, user_factory, password_factory, setting, code_required
):
    password = password_factory()
    user = user_factory(password=password, email_verified=False)
    email_address = EmailAddress.objects.get(email=user.email)
    assert not email_address.verified
    settings.ACCOUNT_LOGIN_BY_CODE_REQUIRED = setting
    resp = client.post(
        reverse("account_login"),
        data={"login": user.username, "password": password},
    )
    assert resp.status_code == 302
    if code_required:
        assert resp["location"] == reverse("account_confirm_login_code")
        code = client.session[LOGIN_SESSION_KEY]["state"][LOGIN_CODE_STATE_KEY]["code"]
        resp = client.get(
            reverse("account_confirm_login_code"),
            data={"login": user.username, "password": password},
        )
        assert resp.status_code == 200
        resp = client.post(reverse("account_confirm_login_code"), data={"code": code})
        email_address.refresh_from_db()
        assert email_address.verified
    assert resp["location"] == settings.LOGIN_REDIRECT_URL


def test_login_by_code_redirect(client, user, request_login_by_code):
    request_login_by_code(client, user.email)
    resp = client.get(reverse("account_login"))
    assert resp["location"] == reverse("account_confirm_login_code")
