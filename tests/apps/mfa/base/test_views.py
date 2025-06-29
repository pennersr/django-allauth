from http import HTTPStatus
from unittest.mock import ANY

from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.mfa.models import Authenticator


def test_reauthentication(auth_client, user_with_recovery_codes):
    resp = auth_client.get(reverse("mfa_view_recovery_codes"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.get(reverse("mfa_reauthenticate"))
    assertTemplateUsed(resp, "mfa/reauthenticate.html")
    authenticator = Authenticator.objects.get(
        user=user_with_recovery_codes, type=Authenticator.Type.RECOVERY_CODES
    )
    unused_code = authenticator.wrap().get_unused_codes()[0]
    resp = auth_client.post(reverse("mfa_reauthenticate"), data={"code": unused_code})
    assert resp.status_code == HTTPStatus.FOUND
    resp = auth_client.get(reverse("mfa_view_recovery_codes"))
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "mfa/recovery_codes/index.html")
    methods = auth_client.session[AUTHENTICATION_METHODS_SESSION_KEY]
    assert methods[-1] == {
        "method": "mfa",
        "type": "recovery_codes",
        "id": authenticator.pk,
        "at": ANY,
        "reauthenticated": True,
    }


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
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"].startswith(reverse("account_login"))


def test_index(auth_client, user_with_totp):
    resp = auth_client.get(reverse("mfa_index"))
    assert "authenticators" in resp.context


@pytest.mark.parametrize("allowed", [False, True])
def test_add_email_not_allowed(
    auth_client,
    user_with_totp,
    settings,
    allowed,
):
    settings.MFA_ALLOW_UNVERIFIED_EMAIL = allowed
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "change-to@this.org"},
    )
    if allowed:
        assert resp.status_code == HTTPStatus.FOUND
    else:
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["form"].errors == {
            "email": [
                "You cannot add an email address to an account protected by two-factor authentication."
            ]
        }


def test_add_email_allowed_when_verification_by_code(
    auth_client,
    user_with_totp,
    settings,
):
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "change-to@this.org"},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_email_verification_sent")
