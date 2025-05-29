from http import HTTPStatus
from unittest.mock import ANY

from django.conf import settings
from django.test import Client
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.adapter import get_adapter
from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY


@pytest.fixture
def phone_only_settings(settings_impacting_urls):
    with settings_impacting_urls(
        ACCOUNT_LOGIN_METHODS=("phone",), ACCOUNT_SIGNUP_FIELDS=["phone*"]
    ):
        yield


def test_signup(db, client, phone, sms_outbox, phone_only_settings):
    assert len(sms_outbox) == 0
    resp = client.post(reverse("account_signup"), data={"phone": phone})
    assert resp.status_code == HTTPStatus.FOUND
    assert len(sms_outbox) == 1
    assert resp["location"] == reverse("account_verify_phone")
    resp = client.get(resp["location"])
    assert resp.status_code == HTTPStatus.OK
    resp = client.post(
        reverse("account_verify_phone"), data={"code": sms_outbox[-1]["code"]}
    )
    assert resp.status_code == HTTPStatus.FOUND
    adapter = get_adapter()
    user = adapter.get_user_by_phone(phone)
    phone2, phone_verified = adapter.get_phone(user)
    assert phone_verified
    assert phone == phone2


def test_signup_invalid_attempts(db, client, phone, sms_outbox, phone_only_settings):
    assert len(sms_outbox) == 0
    resp = client.post(reverse("account_signup"), data={"phone": phone})
    assert resp.status_code == HTTPStatus.FOUND
    adapter = get_adapter()
    user = adapter.get_user_by_phone(phone)
    _, phone_verified = adapter.get_phone(user)
    assert not phone_verified
    assert len(sms_outbox) == 1
    assert resp["location"] == reverse("account_verify_phone")
    resp = client.get(resp["location"])
    assert resp.status_code == HTTPStatus.OK
    for i in range(3):
        resp = client.post(reverse("account_verify_phone"), data={"code": "wrong"})
        assert resp.status_code == (HTTPStatus.OK if i < 2 else HTTPStatus.FOUND)


def test_login_sends_code(
    user_with_phone, client, phone_only_settings, phone, sms_outbox
):
    resp = client.post(reverse("account_login"), data={"login": phone})
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_confirm_login_code")
    assert len(sms_outbox) == 1


def test_login_with_verified_phone_and_password(
    client, settings_impacting_urls, phone, user_with_phone, user_password
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
        ACCOUNT_LOGIN_METHODS=["phone"],
    ):
        resp = client.post(
            reverse("account_login"), data={"login": phone, "password": user_password}
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == settings.LOGIN_REDIRECT_URL


def test_login_with_unverified_phone_and_password(
    client, settings_impacting_urls, phone, password_factory, user_factory, sms_outbox
):
    with settings_impacting_urls(
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
        ACCOUNT_LOGIN_METHODS=["phone"],
    ):
        password = password_factory()
        user = user_factory(phone=phone, password=password, phone_verified=False)
        resp = client.post(
            reverse("account_login"), data={"login": phone, "password": password}
        )
        assert resp.status_code == HTTPStatus.FOUND
        assert resp["location"] == reverse("account_verify_phone")
        code = sms_outbox[-1]["code"]
        resp = client.post(reverse("account_verify_phone"), data={"code": code})
        assert resp["location"] == settings.LOGIN_REDIRECT_URL
        phone_verified = get_adapter().get_phone(user)
        assert phone_verified == (phone, True)


def test_change_phone(
    auth_client, user, phone_only_settings, phone_factory, sms_outbox
):
    new_phone = phone_factory()
    resp = auth_client.get(reverse("account_change_phone"))
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "account/phone_change.html")

    resp = auth_client.post(reverse("account_change_phone"), {"phone": new_phone})
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_verify_phone")

    code = sms_outbox[-1]["code"]
    resp = auth_client.get(reverse("account_verify_phone"))
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "account/confirm_phone_verification_code.html")

    resp = auth_client.post(reverse("account_verify_phone"), {"code": code})
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_change_phone")

    phone_verified = get_adapter().get_phone(user)
    assert phone_verified == (new_phone, True)

    resp = auth_client.get(reverse("account_verify_phone"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_change_phone")


def test_change_phone_to_already_existing(
    auth_client, user, phone_only_settings, phone_factory, sms_outbox, user_factory
):
    other_phone = phone_factory()
    user_factory(phone=other_phone)

    resp = auth_client.post(reverse("account_change_phone"), {"phone": other_phone})
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_verify_phone")

    code = sms_outbox[-1]["code"]
    resp = auth_client.get(reverse("account_verify_phone"))
    assert resp.status_code == HTTPStatus.OK
    assertTemplateUsed(resp, "account/confirm_phone_verification_code.html")

    resp = auth_client.post(reverse("account_verify_phone"), {"code": code})
    assert resp.status_code == HTTPStatus.OK
    assert resp.context["form"].errors == {
        "code": ["A user is already registered with this phone number."]
    }


def test_login_by_code_enumeration_prevention(
    db, phone_only_settings, client, phone_factory, sms_outbox
):
    resp = client.post(
        reverse("account_request_login_code"), data={"phone": phone_factory()}
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_confirm_login_code")
    assert "code" not in sms_outbox[-1]
    assert "user_id" not in sms_outbox[-1]


def test_reauthentication(
    settings,
    auth_client,
    user_with_phone,
    phone_factory,
    settings_impacting_urls,
    user_password,
):
    with settings_impacting_urls(
        ACCOUNT_REAUTHENTICATION_REQUIRED=True,
        ACCOUNT_LOGIN_METHODS=("phone",),
        ACCOUNT_SIGNUP_FIELDS=["phone*", "password1*"],
    ):
        new_phone = phone_factory()
        resp = auth_client.post(
            reverse("account_change_phone"),
            {"phone": new_phone},
        )
        assert resp["location"].startswith(reverse("account_reauthenticate"))

        resp = auth_client.get(reverse("account_reauthenticate"))
        assertTemplateUsed(resp, "account/reauthenticate.html")
        resp = auth_client.post(
            reverse("account_reauthenticate"), data={"password": user_password}
        )
        assert resp.status_code == 302

        methods = auth_client.session[AUTHENTICATION_METHODS_SESSION_KEY]
        assert methods[-1] == {"method": "password", "at": ANY, "reauthenticated": True}

        resp = auth_client.post(
            reverse("account_change_phone"),
            {"phone": new_phone},
        )
        assert resp["location"].startswith(reverse("account_verify_phone"))


def test_signup_conflict(db, phone, sms_outbox, phone_only_settings):
    assert len(sms_outbox) == 0
    client = Client()
    resp = client.post(reverse("account_signup"), data={"phone": phone})
    assert resp.status_code == HTTPStatus.FOUND
    assert len(sms_outbox) == 1

    client = Client()
    resp = client.post(reverse("account_signup"), data={"phone": phone})
    assert resp.status_code == HTTPStatus.FOUND
    assert len(sms_outbox) == 2
    assert sms_outbox == [
        {"code": ANY, "phone": phone, "user_id": 1},
        {"phone": phone, "reason": "exists"},
    ]


def test_change_to_already_existing_phone(
    client,
    db,
    settings,
    phone_factory,
    sms_outbox,
    messagesoutbox,
    user_with_phone,
    phone_only_settings,
):
    settings.ACCOUNT_PHONE_VERIFICATION_SUPPORTS_RESEND = True
    settings.ACCOUNT_PHONE_VERIFICATION_SUPPORTS_CHANGE = True
    settings.ACCOUNT_PREVENT_ENUMERATION = True
    new_phone = phone_factory()
    resp = client.post(
        reverse("account_signup"),
        {"phone": new_phone},
    )
    # A user signed up.
    new_user = get_adapter().get_user_by_phone(new_phone)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_verify_phone")
    assert len(sms_outbox) == 1
    assert sms_outbox[0] == {"code": ANY, "phone": new_phone, "user_id": new_user.pk}
    # assert len(messagesoutbox) == 1
    # assert (
    #     messagesoutbox[-1]["message_template"]
    #     == "account/messages/email_confirmation_sent.txt"
    # )

    # Change to a conflicting phone number
    existing_phone_verified = get_adapter().get_phone(user_with_phone)
    resp = client.post(
        reverse("account_verify_phone"),
        {"action": "change", "phone": existing_phone_verified[0]},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_verify_phone")
    assert len(sms_outbox) == 2
    assert sms_outbox[1] == {"phone": existing_phone_verified[0], "reason": "exists"}
    # assert len(messagesoutbox) == 2
    # assert (
    #     messagesoutbox[-1]["message_template"]
    #     == "account/messages/email_confirmation_sent.txt"
    # )
    assert get_adapter().get_phone(new_user)[0] == new_phone

    # Change back to new phone
    new_phone2 = phone_factory()
    resp = client.post(
        reverse("account_verify_phone"),
        {"action": "change", "phone": new_phone2},
    )
    assert len(sms_outbox) == 3
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_verify_phone")
    assert sms_outbox[2] == {"code": ANY, "phone": new_phone2, "user_id": ANY}
    # assert len(messagesoutbox) == 3
    # assert (
    #     messagesoutbox[-1]["message_template"]
    #     == "account/messages/email_confirmation_sent.txt"
    # )
    assert get_adapter().get_phone(new_user)[0] == new_phone2

    resp = client.post(
        reverse("account_verify_phone"),
        data={"code": sms_outbox[-1]["code"]},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert get_adapter().get_phone(new_user) == (new_phone2, True)


def test_signup_invalid_phone(db, client, sms_outbox, phone_only_settings):
    assert len(sms_outbox) == 0
    resp = client.post(reverse("account_signup"), data={"phone": "notaphone"})
    assert resp.status_code == HTTPStatus.OK
    assert resp.context["form"].errors == {
        "phone": ["Enter a phone number including country code (e.g. +1 for the US)."]
    }
