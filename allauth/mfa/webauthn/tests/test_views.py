from unittest.mock import ANY

from django.conf import settings
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.mfa.models import Authenticator


def test_passkey_login(client, passkey, webauthn_authentication_bypass):
    with webauthn_authentication_bypass(passkey) as credential:
        resp = client.get(
            reverse("mfa_login_webauthn"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert "request_options" in resp.json()
        resp = client.post(
            reverse("mfa_login_webauthn"), data={"credential": credential}
        )
    assert resp["location"] == settings.LOGIN_REDIRECT_URL


def test_reauthenticate(
    auth_client, passkey, user_with_recovery_codes, webauthn_authentication_bypass
):
    resp = auth_client.get(reverse("mfa_view_recovery_codes"))
    assert resp.status_code == 302
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.get(reverse("mfa_reauthenticate"))
    assertTemplateUsed(resp, "mfa/reauthenticate.html")

    with webauthn_authentication_bypass(passkey) as credential:
        resp = auth_client.get(
            reverse("mfa_reauthenticate_webauthn"),
        )
        resp = auth_client.post(
            reverse("mfa_reauthenticate_webauthn"),
            data={"credential": credential, "next": "/redir"},
        )
    assert resp["location"] == "/redir"


def test_get_passkey_login_challenge_redirects_if_not_ajax(client):
    resp = client.get(reverse("mfa_login_webauthn"))
    assert resp["location"] == reverse("account_login")


def test_get_passkey_login_challenge(client, db):
    resp = client.get(
        reverse("mfa_login_webauthn"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert resp.status_code == 200
    assert resp["content-type"] == "application/json"
    data = resp.json()
    assert data == {
        "request_options": {
            "publicKey": {
                "challenge": ANY,
                "rpId": "testserver",
                "allowCredentials": [],
                "userVerification": "preferred",
            }
        }
    }


def test_invalid_passkey_login(client, passkey):
    resp = client.post(reverse("mfa_login_webauthn"), data={"credential": "{}"})
    assert resp["location"] == reverse("account_login")


def test_rename_key(auth_client, passkey, reauthentication_bypass):
    resp = auth_client.get(reverse("mfa_edit_webauthn", kwargs={"pk": passkey.pk}))
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_edit_webauthn", kwargs={"pk": passkey.pk}))
        assertTemplateUsed(resp, "mfa/webauthn/edit_form.html")
        resp = auth_client.post(
            reverse("mfa_edit_webauthn", kwargs={"pk": passkey.pk}),
            data={"name": "Renamed"},
        )
        assert resp["location"] == reverse("mfa_list_webauthn")
        passkey.refresh_from_db()
        assert passkey.data["name"] == "Renamed"
        assert str(passkey) == "Renamed"


def test_remove_key(auth_client, passkey, reauthentication_bypass):
    resp = auth_client.get(reverse("mfa_remove_webauthn", kwargs={"pk": passkey.pk}))
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    with reauthentication_bypass():
        resp = auth_client.get(
            reverse("mfa_remove_webauthn", kwargs={"pk": passkey.pk})
        )
        assertTemplateUsed(resp, "mfa/webauthn/authenticator_confirm_delete.html")
        resp = auth_client.post(
            reverse("mfa_remove_webauthn", kwargs={"pk": passkey.pk})
        )
        assert resp["location"] == reverse("mfa_list_webauthn")


@pytest.mark.parametrize("passwordless", [False, True])
def test_add_key(
    auth_client,
    user,
    webauthn_registration_bypass,
    reauthentication_bypass,
    passwordless,
):
    with webauthn_registration_bypass(user, passwordless) as credential:
        resp = auth_client.post(
            reverse("mfa_add_webauthn"), data={"credential": credential}
        )
        assert resp["location"].startswith(reverse("account_reauthenticate"))
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_add_webauthn"))
        assertTemplateUsed(resp, "mfa/webauthn/add_form.html")
        with webauthn_registration_bypass(user, passwordless) as credential:
            resp = auth_client.post(
                reverse("mfa_add_webauthn"),
                data={
                    "credential": credential,
                    "passwordless": "on" if passwordless else "",
                },
            )
            assert resp["location"].startswith(reverse("mfa_view_recovery_codes"))
        authenticator = Authenticator.objects.get(
            user=user, type=Authenticator.Type.WEBAUTHN
        )
        assert authenticator.wrap().is_passwordless == passwordless
        Authenticator.objects.filter(
            user=user, type=Authenticator.Type.RECOVERY_CODES
        ).exists()


def test_list_keys(auth_client):
    resp = auth_client.get(reverse("mfa_list_webauthn"))
    assertTemplateUsed(resp, "mfa/webauthn/authenticator_list.html")
