import re
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

import pytest

from allauth.account.internal.flows import email_verification_by_code
from allauth.account.models import EmailAddress


@pytest.fixture
def get_last_code(client, mailoutbox):
    def f():
        code = re.search(
            "\n[0-9a-z]{6}\n", mailoutbox[0].body, re.I | re.DOTALL | re.MULTILINE
        )[0].strip()
        assert (
            client.session[
                email_verification_by_code.EMAIL_VERIFICATION_CODE_SESSION_KEY
            ]["code"]
            == code
        )
        return code

    return f


@pytest.fixture(autouse=True)
def email_verification_settings(settings):
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    return settings


@pytest.mark.parametrize(
    "query,expected_url",
    [
        ("", settings.LOGIN_REDIRECT_URL),
        ("?next=/foo", "/foo"),
    ],
)
def test_signup(
    client, db, settings, password_factory, get_last_code, query, expected_url
):
    password = password_factory()
    resp = client.post(
        reverse("account_signup") + query,
        {
            "username": "johndoe",
            "email": "john@example.com",
            "password1": password,
            "password2": password,
        },
    )
    assert get_user_model().objects.filter(username="johndoe").count() == 1
    code = get_last_code()
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_email_verification_sent")
    resp = client.get(reverse("account_email_verification_sent"))
    assert resp.status_code == 200
    resp = client.post(reverse("account_email_verification_sent"), data={"code": code})
    assert resp.status_code == 302
    assert resp["location"] == expected_url


def test_signup_prevent_enumeration(
    client, db, settings, password_factory, user, mailoutbox
):
    password = password_factory()
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": user.email,
            "password1": password,
            "password2": password,
        },
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_email_verification_sent")
    assert not get_user_model().objects.filter(username="johndoe").exists()
    assert mailoutbox[0].subject == "[example.com] Account Already Exists"
    resp = client.get(reverse("account_email_verification_sent"))
    assert resp.status_code == 200
    resp = client.post(reverse("account_email_verification_sent"), data={"code": ""})
    assert resp.status_code == 200
    assert resp.context["form"].errors == {"code": ["This field is required."]}
    resp = client.post(reverse("account_email_verification_sent"), data={"code": "123"})
    assert resp.status_code == 200
    assert resp.context["form"].errors == {"code": ["Incorrect code."]}
    # Max attempts
    resp = client.post(reverse("account_email_verification_sent"), data={"code": "456"})
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_login")


@pytest.mark.parametrize("change_email", (False, True))
def test_add_or_change_email(auth_client, user, get_last_code, change_email, settings):
    settings.ACCOUNT_CHANGE_EMAIL = change_email
    email = "additional@email.org"
    assert EmailAddress.objects.filter(user=user).count() == 1
    with patch("allauth.account.signals.email_added") as email_added_signal:
        with patch("allauth.account.signals.email_changed") as email_changed_signal:
            resp = auth_client.post(
                reverse("account_email"), {"action_add": "", "email": email}
            )
            assert resp["location"] == reverse("account_email_verification_sent")
            assert not email_added_signal.send.called
            assert not email_changed_signal.send.called
    assert EmailAddress.objects.filter(email=email).count() == 0
    code = get_last_code()
    resp = auth_client.get(reverse("account_email_verification_sent"))
    assert resp.status_code == 200
    with patch("allauth.account.signals.email_added") as email_added_signal:
        with patch("allauth.account.signals.email_changed") as email_changed_signal:
            with patch(
                "allauth.account.signals.email_confirmed"
            ) as email_confirmed_signal:
                resp = auth_client.post(
                    reverse("account_email_verification_sent"), data={"code": code}
                )
                assert resp.status_code == 302
                assert resp["location"] == reverse("account_email")
                assert email_added_signal.send.called
                assert email_confirmed_signal.send.called
                assert email_changed_signal.send.called == change_email
    assert EmailAddress.objects.filter(email=email, verified=True).count() == 1
    assert EmailAddress.objects.filter(user=user).count() == (1 if change_email else 2)


def test_email_verification_login_redirect(
    client, db, settings, password_factory, email_verification_settings
):
    password = password_factory()
    resp = client.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": "user@email.org",
            "password1": password,
            "password2": password,
        },
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_email_verification_sent")
    resp = client.get(reverse("account_login"))
    assert resp["location"] == reverse("account_email_verification_sent")


def test_email_verification_rate_limits(
    db,
    user_password,
    email_verification_settings,
    settings,
    user_factory,
    password_factory,
    enable_cache,
):
    settings.ACCOUNT_RATE_LIMITS = {"confirm_email": "1/m/key"}
    email = "user@email.org"
    user_factory(email=email, email_verified=False, password=user_password)
    for attempt in range(2):
        resp = Client().post(
            reverse("account_login"),
            {
                "login": email,
                "password": user_password,
            },
        )
        if attempt == 0:
            assert resp.status_code == 302
            assert resp["location"] == reverse("account_email_verification_sent")
        else:
            assert resp.status_code == 200
            assert resp.context["form"].errors == {
                "__all__": ["Too many failed login attempts. Try again later."]
            }
