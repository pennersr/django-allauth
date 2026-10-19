import time
from http import HTTPStatus
from unittest.mock import ANY, patch

from django.conf import settings
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account import app_settings
from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal.auth import SECRET_SESSION_KEY


def test_activate_totp_with_incorrect_code(auth_client, reauthentication_bypass):
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_activate_totp"))
        resp = auth_client.post(
            reverse("mfa_activate_totp"),
            {
                "code": "123",
            },
        )
    assert resp.context["form"].errors == {
        "code": [get_adapter().error_messages["incorrect_code"]]
    }


def test_activate_totp_rate_limit(
    auth_client, reauthentication_bypass, settings, enable_cache
):
    settings.ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 1
    with reauthentication_bypass():
        auth_client.get(reverse("mfa_activate_totp"))
        for i in range(2):
            is_locked = i >= 1
            resp = auth_client.post(
                reverse("mfa_activate_totp"),
                {
                    "code": "wrong",
                },
            )
            assert resp.context["form"].errors == {
                "code": [
                    (
                        "Be patient, you are sending too many requests."
                        if is_locked
                        else "Incorrect code."
                    )
                ]
            }


@pytest.mark.parametrize("email_verified", [False])
@pytest.mark.parametrize("method", ["get", "post"])
def test_activate_totp_with_unverified_email(
    auth_client, user, totp_validation_bypass, reauthentication_bypass, method
):
    with reauthentication_bypass():
        if method == "get":
            resp = auth_client.get(reverse("mfa_activate_totp"))
        else:
            resp = auth_client.post(reverse("mfa_activate_totp"), {"code": "123"})
    assert resp["location"] == reverse("mfa_index")


def test_activate_totp_success(
    auth_client,
    totp_validation_bypass,
    user,
    reauthentication_bypass,
    settings,
    mailoutbox,
    django_capture_on_commit_callbacks,
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_activate_totp"))
        with totp_validation_bypass():
            with django_capture_on_commit_callbacks(execute=True):
                resp = auth_client.post(
                    reverse("mfa_activate_totp"),
                    {
                        "code": "123",
                    },
                )
    assert resp["location"] == reverse("mfa_view_recovery_codes")
    assert Authenticator.objects.filter(
        user=user, type=Authenticator.Type.TOTP
    ).exists()
    assert Authenticator.objects.filter(
        user=user, type=Authenticator.Type.RECOVERY_CODES
    ).exists()
    assert len(mailoutbox) == 1
    assert "Authenticator App Activated" in mailoutbox[0].subject
    assert "Authenticator app activated." in mailoutbox[0].body
    assert SECRET_SESSION_KEY not in auth_client.session


def test_activate_totp_rolls_back_when_recovery_code_creation_fails(
    auth_client,
    totp_validation_bypass,
    user,
    reauthentication_bypass,
    mailoutbox,
    django_capture_on_commit_callbacks,
):
    with reauthentication_bypass():
        auth_client.get(reverse("mfa_activate_totp"))
        with (
            totp_validation_bypass(),
            patch(
                "allauth.mfa.totp.internal.flows.auto_generate_recovery_codes",
                side_effect=RuntimeError,
            ),
            patch(
                "allauth.mfa.totp.internal.flows.signals.authenticator_added"
            ) as added_signal,
            django_capture_on_commit_callbacks(execute=True),
            pytest.raises(RuntimeError),
        ):
            auth_client.post(reverse("mfa_activate_totp"), {"code": "123"})

    assert not Authenticator.objects.filter(
        user=user, type=Authenticator.Type.TOTP
    ).exists()
    assert not added_signal.send.called
    assert not mailoutbox
    assert SECRET_SESSION_KEY in auth_client.session


def test_deactivate_totp_success(
    auth_client, user_with_totp, user_password, settings, mailoutbox
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    resp = auth_client.get(reverse("mfa_deactivate_totp"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == HTTPStatus.FOUND
    resp = auth_client.post(reverse("mfa_deactivate_totp"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_index")
    assert len(mailoutbox) == 1
    assert "Authenticator App Deactivated" in mailoutbox[0].subject
    assert "Authenticator app deactivated." in mailoutbox[0].body


def test_user_without_totp_deactivate_totp(auth_client):
    resp = auth_client.get(reverse("mfa_deactivate_totp"))
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_user_with_totp_activate_totp(
    auth_client, user_with_totp, reauthentication_bypass
):
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_activate_totp"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_deactivate_totp")


def test_totp_login(client, user_with_totp, user_password, totp_validation_bypass):
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_authenticate")
    resp = client.get(reverse("mfa_authenticate"))
    assert resp.context["request"].user.is_anonymous
    resp = client.post(reverse("mfa_authenticate"), {"code": "123"})
    assert resp.context["form"].errors == {
        "code": [get_adapter().error_messages["incorrect_code"]]
    }
    with totp_validation_bypass():
        resp = client.post(
            reverse("mfa_authenticate"),
            {"code": "123"},
        )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert client.session[AUTHENTICATION_METHODS_SESSION_KEY] == [
        {"method": "password", "at": ANY, "username": user_with_totp.username},
        {"method": "mfa", "at": ANY, "id": ANY, "type": Authenticator.Type.TOTP},
    ]


def test_cancel_mfa_login_clears_authentication_records(
    client, user_with_totp, user_factory, user_password
):
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_authenticate")

    resp = client.post(
        reverse("account_logout"),
        {"next": reverse("account_login")},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_login")

    other_user = user_factory()
    resp = client.post(
        reverse("account_login"),
        {"login": other_user.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert client.session[AUTHENTICATION_METHODS_SESSION_KEY] == [
        {"method": "password", "at": ANY, "username": other_user.username}
    ]


def test_totp_login_rate_limit(
    settings, enable_cache, user_with_totp, user_password, client
):
    settings.ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 3
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_authenticate")
    for i in range(5):
        is_locked = i >= 3
        with patch("allauth.mfa.signals.authentication_failed") as auth_failed_signal:
            resp = client.post(
                reverse("mfa_authenticate"),
                {
                    "code": "wrong",
                },
            )
            signal_called = not is_locked
            assert auth_failed_signal.send.called == signal_called
            if signal_called:
                signal_kwargs = auth_failed_signal.send.call_args[1]
                assert signal_kwargs["user"] == user_with_totp
                assert signal_kwargs["reauthentication"] is False
        assert resp.context["form"].errors == {
            "code": [
                (
                    "Too many failed login attempts. Try again later."
                    if is_locked
                    else "Incorrect code."
                )
            ]
        }


def test_cannot_deactivate_totp(auth_client, user_with_totp, user_password):
    with patch(
        "allauth.mfa.adapter.DefaultMFAAdapter.can_delete_authenticator"
    ) as cda_mock:
        cda_mock.return_value = False
        resp = auth_client.get(reverse("mfa_deactivate_totp"))
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"].startswith(reverse("account_reauthenticate"))
        resp = auth_client.post(resp["location"], {"password": user_password})
        assert resp.status_code == HTTPStatus.FOUND
        resp = auth_client.get(reverse("mfa_deactivate_totp"))
        # When we GET, the form validation error is already on screen
        assert resp.context["form"].errors == {
            "__all__": [get_adapter().error_messages["cannot_delete_authenticator"]],
        }
        # And, when we POST anyway, it does not work
        resp = auth_client.post(reverse("mfa_deactivate_totp"))
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {
            "__all__": [get_adapter().error_messages["cannot_delete_authenticator"]],
        }


def test_totp_code_reuse(
    user_with_totp, user_password, totp_validation_bypass, enable_cache
):
    for code, time_lapse, expect_success in [
        # First use of code, SUCCESS
        ("123", False, True),
        # Second use, no time elapsed: FAIL
        ("123", False, False),
        # Different code, no time elapsed: SUCCESS
        ("456", False, True),
        # Again, previous code, no time elapsed: FAIL
        ("123", False, False),
        # Previous code, but time elapsed: SUCCESS
        ("123", True, True),
    ]:
        if time_lapse:
            cache.clear()
        client = Client()
        resp = client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == reverse("mfa_authenticate")
        # Note that this bypass only bypasses the actual code check, not the
        # re-use check we're testing here.
        with totp_validation_bypass():
            resp = client.post(
                reverse("mfa_authenticate"),
                {"code": code},
            )
        if expect_success:
            assert resp.status_code == HTTPStatus.FOUND
            assert resp["location"] == settings.LOGIN_REDIRECT_URL
        else:
            assert resp.status_code == HTTPStatus.OK
            assert resp.context["form"].errors == {
                "code": [get_adapter().error_messages["incorrect_code"]]
            }


@pytest.mark.parametrize("code", ["123-456", "1 23456"])
def test_totp_code_reuse_with_alternate_representation(
    user_with_totp,
    user_password,
    totp_validation_bypass,
    enable_cache,
    code,
):
    for submitted_code, expect_success in [("123456", True), (code, False)]:
        client = Client()
        resp = client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == reverse("mfa_authenticate")
        with totp_validation_bypass():
            resp = client.post(
                reverse("mfa_authenticate"),
                {"code": submitted_code},
            )

        if expect_success:
            assert resp.status_code == HTTPStatus.FOUND
            assert resp["location"] == settings.LOGIN_REDIRECT_URL
        else:
            assert resp.status_code == HTTPStatus.OK
            assert resp.context["form"].errors == {
                "code": [get_adapter().error_messages["incorrect_code"]]
            }


@pytest.mark.parametrize("code", ["123-456", "1 23456"])
def test_activate_totp_normalizes_code(
    auth_client,
    user,
    reauthentication_bypass,
    code,
):
    with reauthentication_bypass():
        auth_client.get(reverse("mfa_activate_totp"))
        with patch("allauth.mfa.totp.internal.auth.hotp_value", return_value=123456):
            resp = auth_client.post(reverse("mfa_activate_totp"), {"code": code})

    assert resp.status_code == HTTPStatus.FOUND
    assert Authenticator.objects.filter(
        user=user, type=Authenticator.Type.TOTP
    ).exists()


def test_totp_stage_expires(client, user_with_totp, user_password):
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_authenticate")
    resp = client.get(reverse("mfa_authenticate"))
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "mfa/authenticate.html")
    with patch(
        "allauth.account.internal.stagekit.time.time",
        return_value=time.time() + 1.1 * app_settings.LOGIN_TIMEOUT,
    ):
        resp = client.get(reverse("mfa_authenticate"))
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == reverse("account_login")
