from http import HTTPStatus

from django.urls import reverse

import pytest

from allauth.account.models import EmailAddress


@pytest.fixture(autouse=True)
def prbc_settings(settings_impacting_urls):
    with settings_impacting_urls(ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED=True):
        yield


def test_flow(user, client, mailoutbox, get_last_password_reset_code, password_factory):
    new_password = password_factory()
    assert not user.check_password(new_password)
    resp = client.post(reverse("account_reset_password"), {"email": user.email})
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_confirm_password_reset_code")
    resp = client.post(
        reverse("account_confirm_password_reset_code"),
        {"code": get_last_password_reset_code(client, mailoutbox)},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_complete_password_reset")
    resp = client.post(
        reverse("account_complete_password_reset"),
        {"password1": new_password, "password2": new_password},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_password_reset_completed")
    user.refresh_from_db()
    assert user.check_password(new_password)


def test_prevent_enumeration(db, client, mailoutbox):
    resp = client.post(
        reverse("account_reset_password"), {"email": "unknown@account.org"}
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_confirm_password_reset_code")
    assert mailoutbox[0].subject == "[example.com] Unknown Account"
    resp = client.post(
        reverse("account_confirm_password_reset_code"),
        {"code": "none?"},
    )
    assert resp.status_code == HTTPStatus.OK


def test_indirect_email_verification(
    db, client, mailoutbox, user_factory, get_last_password_reset_code
):
    user = user_factory(email_verified=False)
    address = EmailAddress.objects.get(user=user, email=user.email, verified=False)
    resp = client.post(reverse("account_reset_password"), {"email": address.email})
    assert resp.status_code == HTTPStatus.FOUND
    resp = client.post(
        reverse("account_confirm_password_reset_code"),
        {"code": get_last_password_reset_code(client, mailoutbox)},
    )
    assert resp.status_code == HTTPStatus.FOUND
    address.refresh_from_db()
    assert address.verified
