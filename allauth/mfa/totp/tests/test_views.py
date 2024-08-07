from unittest.mock import ANY, patch

from django.conf import settings
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.account.models import EmailAddress
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator
import time
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal.auth import hotp_counter_from_time, hotp_value


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
    auth_client,
    totp_validation_bypass,
    user,
    reauthentication_bypass,
    settings,
    mailoutbox,
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
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
    assert len(mailoutbox) == 1
    assert "Authenticator App Activated" in mailoutbox[0].subject
    assert "Authenticator app activated." in mailoutbox[0].body


def test_deactivate_totp_success(
    auth_client, user_with_totp, user_password, settings, mailoutbox
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    resp = auth_client.get(reverse("mfa_deactivate_totp"))
    assert resp.status_code == 302
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == 302
    resp = auth_client.post(reverse("mfa_deactivate_totp"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("mfa_index")
    assert len(mailoutbox) == 1
    assert "Authenticator App Deactivated" in mailoutbox[0].subject
    assert "Authenticator app deactivated." in mailoutbox[0].body


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


@override_settings(ACCOUNT_LOGIN_ATTEMPTS_LIMIT=None)
def test_totp_time_tolerance(user_with_totp, user_password, enable_cache):
    client = Client()
    auth = Authenticator.objects.get(user=user_with_totp, type=Authenticator.Type.TOTP)
    secret = auth.wrap().instance.data["secret"]

    def login_with_code(code):
        client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        resp = client.post(reverse("mfa_authenticate"), {"code": code})
        return resp.status_code == 302

    current_counter = hotp_counter_from_time()

    # Test current time step
    current_code = f"{hotp_value(secret, current_counter):06d}"
    assert login_with_code(current_code)

    # Test one step in the past
    past_code = f"{hotp_value(secret, current_counter - 1):06d}"
    assert login_with_code(past_code)

    # Test one step in the future
    future_code = f"{hotp_value(secret, current_counter + 1):06d}"
    assert login_with_code(future_code)

    # Test two steps in the past (should fail with default tolerance)
    past_code_2 = f"{hotp_value(secret, current_counter - 2):06d}"
    assert not login_with_code(past_code_2)

    # Test two steps in the future (should fail with default tolerance)
    future_code_2 = f"{hotp_value(secret, current_counter + 2):06d}"
    assert not login_with_code(future_code_2)
    client = Client()
    auth = Authenticator.objects.get(user=user_with_totp, type=Authenticator.Type.TOTP)
    secret = auth.wrap().instance.data["secret"]

    def login_with_code(code):
        client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        resp = client.post(reverse("mfa_authenticate"), {"code": code})
        return resp.status_code == 302

    current_counter = hotp_counter_from_time()

    # Test current time step
    current_code = f"{hotp_value(secret, current_counter):06d}"
    assert login_with_code(current_code)

    # Test one step in the past
    past_code = f"{hotp_value(secret, current_counter - 1):06d}"
    assert login_with_code(past_code)

    # Test one step in the future
    future_code = f"{hotp_value(secret, current_counter + 1):06d}"
    assert login_with_code(future_code)

    # Test two steps in the past (should fail with default tolerance)
    past_code_2 = f"{hotp_value(secret, current_counter - 2):06d}"
    assert not login_with_code(past_code_2)

    # Test two steps in the future (should fail with default tolerance)
    future_code_2 = f"{hotp_value(secret, current_counter + 2):06d}"
    assert not login_with_code(future_code_2)

@override_settings(ACCOUNT_LOGIN_ATTEMPTS_LIMIT=None)
def test_totp_custom_time_tolerance(user_with_totp, user_password, enable_cache):
    client = Client()
    auth = Authenticator.objects.get(user=user_with_totp, type=Authenticator.Type.TOTP)
    secret = auth.wrap().instance.data["secret"]

    def login_with_code(code):
        client.post(
            reverse("account_login"),
            {"login": user_with_totp.username, "password": user_password},
        )
        resp = client.post(reverse("mfa_authenticate"), {"code": code})
        return resp.status_code == 302

    current_counter = hotp_counter_from_time()

    with override_settings(MFA_TOTP_TIME_TOLERANCE=2):
        # Test two steps in the past (should succeed with tolerance=2)
        past_code_2 = f"{hotp_value(secret, current_counter - 2):06d}"
        assert login_with_code(past_code_2)

        # Test two steps in the future (should succeed with tolerance=2)
        future_code_2 = f"{hotp_value(secret, current_counter + 2):06d}"
        assert login_with_code(future_code_2)

        # Test three steps in the past (should fail with tolerance=2)
        past_code_3 = f"{hotp_value(secret, current_counter - 3):06d}"
        assert not login_with_code(past_code_3)

        # Test three steps in the future (should fail with tolerance=2)
        future_code_3 = f"{hotp_value(secret, current_counter + 3):06d}"
        assert not login_with_code(future_code_3)

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
        assert resp.status_code == 302
        assert resp["location"] == reverse("mfa_authenticate")
        # Note that this bypass only bypasses the actual code check, not the
        # re-use check we're testing here.
        with totp_validation_bypass():
            resp = client.post(
                reverse("mfa_authenticate"),
                {"code": code},
            )
        if expect_success:
            assert resp.status_code == 302
            assert resp["location"] == settings.LOGIN_REDIRECT_URL
        else:
            assert resp.status_code == 200
            assert resp.context["form"].errors == {
                "code": [get_adapter().error_messages["incorrect_code"]]
            }