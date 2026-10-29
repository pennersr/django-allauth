from http import HTTPStatus
from unittest.mock import ANY

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.authentication import get_authentication_records
from allauth.mfa import app_settings as mfa_app_settings
from allauth.mfa.adapter import get_adapter
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
    assert get_authentication_records(resp.wsgi_request, passkey.user) == [
        {
            "at": ANY,
            "id": ANY,
            "method": "mfa",
            "passwordless": True,
            "type": "webauthn",
        }
    ]


def test_inactive_passkey_login_does_not_bypass_mfa_for_next_user(
    client,
    user_with_passkey,
    user_factory,
    user_password,
    webauthn_authentication_bypass,
):
    inactive_user = user_factory(is_active=False)
    inactive_passkey = Authenticator.objects.create(
        user=inactive_user,
        type=Authenticator.Type.WEBAUTHN,
        data={
            "name": "Inactive user's passkey",
            "passwordless": True,
            "credential": {},
        },
    )

    with webauthn_authentication_bypass(inactive_passkey) as credential:
        resp = client.get(
            reverse("mfa_login_webauthn"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        assert resp.status_code == HTTPStatus.OK
        resp = client.post(
            reverse("mfa_login_webauthn"), data={"credential": credential}
        )

    assert resp["location"] == reverse("account_inactive")
    assert get_authentication_records(resp.wsgi_request, inactive_user) == []

    resp = client.post(
        reverse("account_login"),
        {"login": user_with_passkey.username, "password": user_password},
    )

    assert resp["location"] == reverse("mfa_authenticate")


@pytest.mark.parametrize("user_verification", ["preferred", "required"])
def test_reauthenticate(
    auth_client,
    passkey,
    user_with_recovery_codes,
    webauthn_authentication_bypass,
    settings,
    user_verification,
):
    settings.MFA_WEBAUTHN_USER_VERIFICATION = user_verification
    resp = auth_client.get(reverse("mfa_view_recovery_codes"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    resp = auth_client.get(reverse("mfa_reauthenticate"))
    assertTemplateUsed(resp, "mfa/reauthenticate.html")

    with webauthn_authentication_bypass(passkey) as credential:
        resp = auth_client.get(reverse("mfa_reauthenticate_webauthn"))
        assert (
            resp.context["js_data"]["request_options"]["publicKey"]["userVerification"]
            == user_verification
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
    assert resp.status_code == HTTPStatus.OK
    assert resp["content-type"] == "application/json"
    data = resp.json()
    assert data == {
        "request_options": {
            "publicKey": {
                "challenge": ANY,
                "rpId": "testserver",
                "allowCredentials": [],
                "userVerification": "required",
            }
        }
    }


def test_invalid_user_verification_setting(settings):
    settings.MFA_WEBAUTHN_USER_VERIFICATION = "invalid"
    with pytest.raises(ImproperlyConfigured):
        mfa_app_settings.WEBAUTHN_USER_VERIFICATION


def test_invalid_passkey_login(client, passkey):
    resp = client.post(reverse("mfa_login_webauthn"), data={"credential": "{}"})
    assert resp["location"] == reverse("account_login")


def test_passkey_login_rate_limit_applies_before_parsing(
    client, settings, enable_cache
):
    settings.MFA_RATE_LIMITS = {"webauthn_login": "1/m/ip"}
    url = reverse("mfa_login_webauthn")

    resp = client.post(url, data={"credential": "{}"})
    assert resp["location"] == reverse("account_login")

    resp = client.post(url, data={"credential": "{}"})
    assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS


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


def test_add_passwordless_key_requires_user_verification(
    auth_client,
    user,
    webauthn_registration_bypass,
    reauthentication_bypass,
):
    with reauthentication_bypass():
        auth_client.get(reverse("mfa_add_webauthn"))
        with webauthn_registration_bypass(
            user, passwordless=True, user_verified=False
        ) as credential:
            resp = auth_client.post(
                reverse("mfa_add_webauthn"),
                data={"credential": credential, "passwordless": "on"},
            )

    assert resp.status_code == HTTPStatus.OK
    assert resp.context["form"].errors == {
        "__all__": [get_adapter().error_messages["incorrect_code"]]
    }
    assert not Authenticator.objects.filter(
        user=user, type=Authenticator.Type.WEBAUTHN
    ).exists()


@pytest.mark.parametrize("user_verification", ["discouraged", "preferred", "required"])
def test_get_add_key_user_verification(
    auth_client,
    reauthentication_bypass,
    settings,
    user_verification,
):
    settings.MFA_WEBAUTHN_USER_VERIFICATION = user_verification
    with reauthentication_bypass():
        resp = auth_client.get(reverse("mfa_add_webauthn"))

    assert (
        resp.context["js_data"]["creation_options"]["publicKey"][
            "authenticatorSelection"
        ]["userVerification"]
        == user_verification
    )


def test_list_keys(auth_client):
    resp = auth_client.get(reverse("mfa_list_webauthn"))
    assertTemplateUsed(resp, "mfa/webauthn/authenticator_list.html")


@pytest.mark.parametrize("email_verified", [False])
@pytest.mark.parametrize("method", ["get", "post"])
@pytest.mark.parametrize("allowed", [True, False])
def test_add_with_unverified_email(
    auth_client,
    user,
    webauthn_registration_bypass,
    reauthentication_bypass,
    method,
    allowed,
    settings,
):
    settings.MFA_ALLOW_UNVERIFIED_EMAIL = allowed
    with webauthn_registration_bypass(user, False) as credential:
        if method == "get":
            resp = auth_client.get(reverse("mfa_add_webauthn"))
        else:
            resp = auth_client.post(
                reverse("mfa_add_webauthn"), data={"credential": credential}
            )
        if allowed:
            assert resp["location"].startswith(reverse("account_reauthenticate"))
        else:
            assert resp["location"] == reverse("mfa_index")


def test_passkey_signup(client, db, webauthn_registration_bypass):
    resp = client.post(
        reverse("account_signup_by_passkey"),
        data={"email": "pass@key.org", "username": "passkey"},
    )
    assert resp["location"] == reverse("mfa_signup_webauthn")
    resp = client.post(resp["location"])
    assert resp.status_code == HTTPStatus.OK
    user = get_user_model().objects.get(email="pass@key.org")
    with webauthn_registration_bypass(user, True) as credential:
        resp = client.post(
            reverse("mfa_signup_webauthn"), data={"credential": credential}
        )
    assert resp["location"] == settings.LOGIN_REDIRECT_URL


def test_login_webauthn_when_already_authenticated(auth_client, passkey):
    """Visiting the WebAuthn login page as a logged-in user should redirect,
    not crash."""
    resp = auth_client.get(reverse("mfa_login_webauthn"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == settings.LOGIN_REDIRECT_URL


def test_webauthn_login(
    client, user_with_passkey, passkey, user_password, webauthn_authentication_bypass
):
    resp = client.post(
        reverse("account_login"),
        {"login": user_with_passkey.username, "password": user_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("mfa_authenticate")
    with webauthn_authentication_bypass(passkey) as credential:
        resp = client.get(reverse("mfa_authenticate"))
        assert resp.status_code == HTTPStatus.OK
        resp = client.post(reverse("mfa_authenticate"), {"credential": credential})
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert get_authentication_records(resp.wsgi_request, user_with_passkey) == [
        {
            "method": "password",
            "at": ANY,
            "username": user_with_passkey.username,
        },
        {
            "method": "mfa",
            "at": ANY,
            "id": ANY,
            "type": Authenticator.Type.WEBAUTHN,
        },
    ]
