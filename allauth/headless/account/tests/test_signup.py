from unittest.mock import ANY, patch

from django.contrib.auth.models import User

from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.headless.constants import Flow


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
        headless_reverse("headless:account:signup"),
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
        headless_reverse("headless:account:signup"),
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
        headless_reverse("headless:account:verify_email"),
        HTTP_X_EMAIL_VERIFICATION_KEY=key,
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
        headless_reverse("headless:account:verify_email"),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["is_authenticated"]
    addr.refresh_from_db()
    assert addr.verified


def test_signup_prevent_enumeration(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
    user,
    mailoutbox,
):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_PREVENT_ENUMERATION = True
    resp = client.post(
        headless_reverse("headless:account:signup"),
        data={
            "email": user.email,
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert len(mailoutbox) == 1
    assert "an account using that email address already exists" in mailoutbox[0].body
    assert resp.status_code == 401
    data = resp.json()
    assert [f for f in data["data"]["flows"] if f["id"] == Flow.VERIFY_EMAIL][0][
        "is_pending"
    ]
    resp = client.get(headless_reverse("headless:account:current_session"))
    data = resp.json()
    assert [f for f in data["data"]["flows"] if f["id"] == Flow.VERIFY_EMAIL][0][
        "is_pending"
    ]


def test_signup_rate_limit(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    enable_cache,
    headless_client,
):
    settings.ACCOUNT_RATE_LIMITS = {"signup": "1/m/ip"}
    for attempt in range(2):
        resp = client.post(
            headless_reverse("headless:account:signup"),
            data={
                "username": f"wizard{attempt}",
                "email": email_factory(),
                "password": password_factory(),
            },
            content_type="application/json",
        )
        expected_status = 429 if attempt else 200
        assert resp.status_code == expected_status
        assert resp.json()["status"] == expected_status


def test_signup_closed(
    db,
    client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
):
    with patch(
        "allauth.account.adapter.DefaultAccountAdapter.is_open_for_signup"
    ) as iofs:
        iofs.return_value = False
        resp = client.post(
            headless_reverse("headless:account:signup"),
            data={
                "username": "wizard",
                "email": email_factory(),
                "password": password_factory(),
            },
            content_type="application/json",
        )
    assert resp.status_code == 403
    assert not User.objects.filter(username="wizard").exists()


def test_signup_while_logged_in(
    db,
    auth_client,
    email_factory,
    password_factory,
    settings,
    headless_reverse,
    headless_client,
):
    resp = auth_client.post(
        headless_reverse("headless:account:signup"),
        data={
            "username": "wizard",
            "email": email_factory(),
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == 409
    assert resp.json() == {"status": 409}
