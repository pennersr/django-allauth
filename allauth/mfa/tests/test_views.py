from django.conf import settings
from django.urls import reverse

import pytest

from allauth.account.models import EmailAddress
from allauth.mfa.adapter import get_adapter


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


def test_activate_totp_with_incorrect_code(auth_client):
    resp = auth_client.get(reverse("mfa_activate_totp"))
    resp = auth_client.post(
        reverse("mfa_activate_totp"),
        {"code": "123", "signed_secret": resp.context["form"].initial["signed_secret"]},
    )
    assert resp.context["form"].errors == {
        "code": [get_adapter().error_messages["incorrect_code"]]
    }


def test_activate_totp_with_tampered_secret(auth_client):
    resp = auth_client.post(
        reverse("mfa_activate_totp"), {"code": "123", "signed_secret": "tampered"}
    )
    assert resp.context["form"].errors == {"signed_secret": ["Tampered form."]}


def test_activate_totp_with_unverified_email(auth_client, user, totp_validation_bypass):
    EmailAddress.objects.filter(user=user).update(verified=False)
    resp = auth_client.get(reverse("mfa_activate_totp"))
    with totp_validation_bypass():
        resp = auth_client.post(
            reverse("mfa_activate_totp"),
            {
                "code": "123",
                "signed_secret": resp.context["form"].initial["signed_secret"],
            },
        )
    assert resp.context["form"].errors == {
        "__all__": [get_adapter().error_messages["unverified_email"]],
    }


def test_activate_totp_success(auth_client, totp_validation_bypass):
    resp = auth_client.get(reverse("mfa_activate_totp"))
    with totp_validation_bypass():
        resp = auth_client.post(
            reverse("mfa_activate_totp"),
            {
                "code": "123",
                "signed_secret": resp.context["form"].initial["signed_secret"],
            },
        )
    assert resp["location"] == reverse("mfa_index")


def test_user_without_totp_deactivate_totp(auth_client):
    resp = auth_client.get(reverse("mfa_deactivate_totp"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("mfa_activate_totp")


def test_user_with_totp_activate_totp(auth_client, user_with_totp):
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
