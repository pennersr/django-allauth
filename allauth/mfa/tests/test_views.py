from unittest.mock import ANY, patch

import django
from django.conf import settings
from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.account.models import EmailAddress
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator


@pytest.mark.parametrize(
    "url_name",
    (
        "mfa_activate_totp",
        "mfa_index",
        "mfa_deactivate_totp",
    ),
)
def test_login_required_views(client, url_name):
    resp = client.get(reverse(url_name))
    assert resp.status_code == 302
    assert resp["location"].startswith(reverse("account_login"))


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


def test_activate_totp_with_unverified_email(
    auth_client, user, totp_validation_bypass, reauthentication_bypass
):
    EmailAddress.objects.filter(user=user).update(verified=False)
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_activate_totp"))
        with totp_validation_bypass():
            resp = auth_client.post(
                reverse("mfa_activate_totp"),
                {
                    "code": "123",
                },
            )
    assert resp.context["form"].errors == {
        "code": [get_adapter().error_messages["unverified_email"]],
    }


def test_activate_totp_success(
    auth_client, totp_validation_bypass, user, reauthentication_bypass
):
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_activate_totp"))
        with totp_validation_bypass():
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


def test_index(auth_client, user_with_totp):
    resp = auth_client.get(reverse("mfa_index"))
    assert "authenticators" in resp.context


def test_deactivate_totp_success(auth_client, user_with_totp, user_password):
    resp = auth_client.get(reverse("mfa_deactivate_totp"))
    assert resp.status_code == 302
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == 302
    resp = auth_client.post(reverse("mfa_deactivate_totp"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("mfa_index")


def test_user_without_totp_deactivate_totp(auth_client):
    resp = auth_client.get(reverse("mfa_deactivate_totp"))
    assert resp.status_code == 404


def test_user_with_totp_activate_totp(
    auth_client, user_with_totp, reauthentication_bypass
):
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_activate_totp"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("mfa_deactivate_totp")


def test_totp_login(client, user_with_totp, user_password, totp_validation_bypass):
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == 302
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
    assert resp.status_code == 302
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert client.session[AUTHENTICATION_METHODS_SESSION_KEY] == [
        {"method": "password", "at": ANY, "username": user_with_totp.username},
        {"method": "mfa", "at": ANY, "id": ANY, "type": Authenticator.Type.TOTP},
    ]


def test_download_recovery_codes(auth_client, user_with_recovery_codes, user_password):
    resp = auth_client.get(reverse("mfa_download_recovery_codes"))
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == 302
    resp = auth_client.get(resp["location"])
    assert resp["content-disposition"] == 'attachment; filename="recovery-codes.txt"'


def test_view_recovery_codes(auth_client, user_with_recovery_codes, user_password):
    resp = auth_client.get(reverse("mfa_view_recovery_codes"))
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == 302
    resp = auth_client.get(resp["location"])
    assert len(resp.context["unused_codes"]) == app_settings.RECOVERY_CODE_COUNT


def test_generate_recovery_codes(auth_client, user_with_recovery_codes, user_password):
    rc = Authenticator.objects.get(
        user=user_with_recovery_codes, type=Authenticator.Type.RECOVERY_CODES
    ).wrap()
    prev_code = rc.get_unused_codes()[0]

    resp = auth_client.get(reverse("mfa_generate_recovery_codes"))
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == 302
    resp = auth_client.post(resp["location"])
    assert resp["location"] == reverse("mfa_view_recovery_codes")

    rc = Authenticator.objects.get(
        user=user_with_recovery_codes, type=Authenticator.Type.RECOVERY_CODES
    ).wrap()
    assert not rc.validate_code(prev_code)


def test_recovery_codes_login(
    client, user_with_totp, user_with_recovery_codes, user_password
):
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("mfa_authenticate")
    resp = client.get(reverse("mfa_authenticate"))
    assert resp.context["request"].user.is_anonymous
    resp = client.post(reverse("mfa_authenticate"), {"code": "123"})
    assert resp.context["form"].errors == {
        "code": [get_adapter().error_messages["incorrect_code"]]
    }
    rc = Authenticator.objects.get(
        user=user_with_recovery_codes, type=Authenticator.Type.RECOVERY_CODES
    )
    resp = client.post(
        reverse("mfa_authenticate"),
        {"code": rc.wrap().get_unused_codes()[0]},
    )
    assert resp.status_code == 302
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert client.session[AUTHENTICATION_METHODS_SESSION_KEY] == [
        {"method": "password", "at": ANY, "username": user_with_totp.username},
        {
            "method": "mfa",
            "at": ANY,
            "id": ANY,
            "type": Authenticator.Type.RECOVERY_CODES,
        },
    ]


def test_add_email_not_allowed(auth_client, user_with_totp):
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "change-to@this.org"},
    )
    assert resp.status_code == 200
    assert resp.context["form"].errors == {
        "email": [
            "You cannot add an email address to an account protected by two-factor authentication."
        ]
    }


def test_totp_login_rate_limit(
    settings, enable_cache, user_with_totp, user_password, client
):
    settings.ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 3
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_totp.username, "password": user_password},
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("mfa_authenticate")
    for i in range(5):
        is_locked = i >= 3
        resp = client.post(
            reverse("mfa_authenticate"),
            {
                "code": "wrong",
            },
        )
        if django.VERSION >= (4, 1):
            assertFormError(
                resp.context["form"],
                "code",
                "Too many failed login attempts. Try again later."
                if is_locked
                else "Incorrect code.",
            )
        else:
            assertFormError(
                resp,
                "form",
                "code",
                "Too many failed login attempts. Try again later."
                if is_locked
                else "Incorrect code.",
            )


def test_cannot_deactivate_totp(auth_client, user_with_totp, user_password):
    with patch(
        "allauth.mfa.adapter.DefaultMFAAdapter.can_delete_authenticator"
    ) as cda_mock:
        cda_mock.return_value = False
        resp = auth_client.get(reverse("mfa_deactivate_totp"))
        assert resp.status_code == 302
        assert resp["location"].startswith(reverse("account_reauthenticate"))
        resp = auth_client.post(resp["location"], {"password": user_password})
        assert resp.status_code == 302
        resp = auth_client.get(reverse("mfa_deactivate_totp"))
        # When we GET, the form validation error is already on screen
        assert resp.context["form"].errors == {
            "__all__": [get_adapter().error_messages["cannot_delete_authenticator"]],
        }
        # And, when we POST anyway, it does not work
        resp = auth_client.post(reverse("mfa_deactivate_totp"))
        assert resp.status_code == 200
        assert resp.context["form"].errors == {
            "__all__": [get_adapter().error_messages["cannot_delete_authenticator"]],
        }
