from django.urls import reverse

from allauth.account.models import EmailAddress, get_emailconfirmation_model


def test_auth_unverified_email_and_mfa(
    client, user_factory, password_factory, settings, totp_validation_bypass
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    password = password_factory()
    user = user_factory(email_verified=False, password=password, with_totp=True)
    resp = client.post(
        reverse("headless_login", args=["browser"]),
        data={
            "email": user.email,
            "password": password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 401
    # FIXME
    # assert resp.json() == {}
    emailaddress = EmailAddress.objects.filter(user=user, verified=False).get()
    key = get_emailconfirmation_model().create(emailaddress).key
    resp = client.post(
        reverse("headless_verify_email", args=["browser"]),
        data={"key": key},
        content_type="application/json",
    )
    assert resp.status_code == 401
    assert resp.json() == {
        "data": {
            "flows": [
                {"id": "login", "url": reverse("headless_login", args=["browser"])},
                {"id": "signup", "url": reverse("headless_signup", args=["browser"])},
                {
                    "id": "provider_login",
                    "url": reverse("headless_redirect_to_provider", args=["browser"]),
                },
                {
                    "id": "mfa_authenticate",
                    "url": reverse("headless_mfa_authenticate", args=["browser"]),
                    "is_pending": True,
                },
            ]
        },
        "meta": {"is_authenticated": False},
        "status": 401,
    }
    resp = client.post(
        reverse("headless_mfa_authenticate", args=["browser"]),
        data={"code": "bad"},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "error": {"detail": {"code": ["Incorrect code."]}},
    }

    with totp_validation_bypass():
        resp = client.post(
            reverse("headless_mfa_authenticate", args=["browser"]),
            data={"code": "bad"},
            content_type="application/json",
        )
    assert resp.status_code == 200
