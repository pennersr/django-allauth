from unittest.mock import ANY

from django.conf import settings
from django.urls import reverse

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.mfa import app_settings
from allauth.mfa.adapter import get_adapter
from allauth.mfa.models import Authenticator


def test_generate_recovery_codes_require_other_authenticator(
    auth_client, user, settings, reauthentication_bypass
):
    with reauthentication_bypass():
        resp = auth_client.post(reverse("mfa_generate_recovery_codes"))
    assert resp.context["form"].errors == {
        "__all__": [
            "You cannot generate recovery codes without having two-factor authentication enabled."
        ]
    }
    assert not Authenticator.objects.filter(user=user).exists()


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


def test_generate_recovery_codes(
    auth_client, user_with_recovery_codes, user_password, settings, mailoutbox
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
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
    assert len(mailoutbox) == 1
    assert "New Recovery Codes Generated" in mailoutbox[0].subject
    assert "A new set of" in mailoutbox[0].body


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
