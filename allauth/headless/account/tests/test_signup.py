from unittest.mock import ANY

from django.contrib.auth.models import User

from allauth.account.models import EmailAddress, EmailConfirmationHMAC


def test_signup(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
):
    resp = client.post(
        headless_reverse("headless:signup"),
        data={
            "username": "wizard",
            "email": email_factory(),
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert User.objects.filter(username="wizard").exists()


def test_signup_with_email_verification(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_USERNAME_REQUIRED = False
    email = email_factory()
    resp = client.post(
        headless_reverse("headless:signup"),
        data={
            "email": email,
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    assert User.objects.filter(email=email).exists()
    data = resp.json()
    flow = next((f for f in data["data"]["flows"] if f.get("is_pending")))
    assert flow["id"] == "verify_email"
    addr = EmailAddress.objects.get(email=email)
    key = EmailConfirmationHMAC(addr).key
    resp = client.get(
        headless_reverse("headless:verify_email"),
        headers={
            "x-email-verification-key": key,
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "data": {
            "email": email,
            "user": ANY,
        },
        "meta": {"is_authenticating": True},
        "status": 200,
    }
    resp = client.post(
        headless_reverse("headless:verify_email"),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["is_authenticated"]
    addr.refresh_from_db()
    assert addr.verified
