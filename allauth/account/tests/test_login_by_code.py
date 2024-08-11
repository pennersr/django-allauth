from unittest.mock import ANY

from django.contrib.auth import SESSION_KEY
from django.urls import reverse

import pytest

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.account.internal.flows.login_by_code import LOGIN_CODE_SESSION_KEY


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
        code = client.session[LOGIN_CODE_SESSION_KEY]["code"]
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
    assert client.session[SESSION_KEY] == str(user.pk)
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
            assert LOGIN_CODE_SESSION_KEY not in client.session
        else:
            assert resp.status_code == 200
            assert LOGIN_CODE_SESSION_KEY in client.session
            assert resp.context["form"].errors == {"code": ["Incorrect code."]}


def test_login_by_code_unknown_user(mailoutbox, client, db):
    resp = client.post(
        reverse("account_request_login_code"),
        data={"email": "unknown@email.org"},
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_confirm_login_code")
    resp = client.post(reverse("account_confirm_login_code"), data={"code": "123456"})
