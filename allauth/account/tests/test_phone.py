from http import HTTPStatus

from django.urls import reverse

import pytest

from allauth.account.adapter import get_adapter


@pytest.fixture
def phone():
    return "+31612345678"


@pytest.fixture(autouse=True)
def phone_settings(settings):
    settings.ACCOUNT_SIGNUP_FIELDS = ["phone", "password1"]


def test_signup(db, client, phone, sms_outbox):
    assert len(sms_outbox) == 0
    resp = client.post(
        reverse("account_signup"), data={"phone": phone, "password1": ""}
    )
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


def test_signup_invalid_attempts(db, client, phone, sms_outbox):
    assert len(sms_outbox) == 0
    resp = client.post(
        reverse("account_signup"), data={"phone": phone, "password1": ""}
    )
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
