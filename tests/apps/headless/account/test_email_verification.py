from http import HTTPStatus

import pytest

from allauth.account.models import (
    EmailAddress,
    EmailConfirmationHMAC,
    get_emailconfirmation_model,
)
from allauth.headless.constants import Flow


def test_verify_email_other_user(auth_client, user, user_factory, headless_reverse):
    other_user = user_factory(email_verified=False)
    email_address = EmailAddress.objects.get(user=other_user, verified=False)
    assert not email_address.verified
    key = EmailConfirmationHMAC(email_address).key
    resp = auth_client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    # We're still authenticated as the user originally logged in, not the
    # other_user.
    assert data["data"]["user"]["id"] == user.pk


@pytest.mark.parametrize(
    "login_on_email_verification,status_code",
    [(False, HTTPStatus.UNAUTHORIZED), (True, HTTPStatus.OK)],
)
def test_auth_unverified_email(
    client,
    user_factory,
    password_factory,
    settings,
    headless_reverse,
    login_on_email_verification,
    status_code,
):
    settings.ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = login_on_email_verification
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    password = password_factory()
    user = user_factory(email_verified=False, password=password)
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    data = resp.json()
    flows = data["data"]["flows"]
    assert [f for f in flows if f["id"] == Flow.VERIFY_EMAIL][0]["is_pending"]
    emailaddress = EmailAddress.objects.filter(user=user, verified=False).get()
    key = get_emailconfirmation_model().create(emailaddress).key
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == status_code


def test_verify_email_bad_key(
    client, settings, password_factory, user_factory, headless_reverse
):
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    password = password_factory()
    user = user_factory(email_verified=False, password=password)
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    resp = client.get(
        headless_reverse("headless:account:verify_email"),
        data={"key": "bad"},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": "bad"},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [
            {
                "code": "invalid_or_expired_key",
                "param": "key",
                "message": "Invalid or expired key.",
            }
        ],
    }
