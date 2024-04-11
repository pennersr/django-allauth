from django.contrib.auth import SESSION_KEY
from django.urls import reverse

import pytest


@pytest.fixture
def request_login_by_email(mailoutbox):
    def f(client, email):
        resp = client.get(reverse("account_login_by_email") + "?next=/foo")
        assert resp.status_code == 200
        assert b'value="/foo"' in resp.content
        resp = client.post(
            reverse("account_login_by_email"), data={"email": email, "next": "/foo"}
        )
        assert resp.status_code == 302
        assert (
            resp["location"]
            == reverse("account_confirm_login_by_email") + "?next=%2Ffoo"
        )
        assert len(mailoutbox) == 1
        code = client.session["account_login_by_email"]["code"]
        assert len(code) == 6
        assert code in mailoutbox[0].body
        return code

    return f


def test_login_by_email(client, user, request_login_by_email):
    code = request_login_by_email(client, user.email)
    code_with_ws = " " + code[0:3] + " " + code[3:]
    resp = client.post(
        reverse("account_confirm_login_by_email"),
        data={"code": code_with_ws, "next": "/foo"},
    )
    assert resp.status_code == 302
    assert client.session[SESSION_KEY] == str(user.pk)
    assert resp["location"] == "/foo"


def test_login_by_email_max_attempts(client, user, request_login_by_email, settings):
    settings.ACCOUNT_LOGIN_BY_EMAIL_MAX_ATTEMPTS = 2
    request_login_by_email(client, user.email)
    for i in range(3):
        resp = client.post(
            reverse("account_confirm_login_by_email"), data={"code": "wrong"}
        )
        if i >= 1:
            assert resp.status_code == 302
            assert resp["location"] == reverse("account_login_by_email")
            assert "account_login_by_email" not in client.session
        else:
            assert resp.status_code == 200
            assert "account_login_by_email" in client.session
            assert resp.context["form"].errors == {"code": ["Incorrect code."]}
