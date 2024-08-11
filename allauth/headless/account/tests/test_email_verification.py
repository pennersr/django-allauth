from allauth.account.models import EmailAddress, get_emailconfirmation_model
from allauth.headless.constants import Flow


def test_auth_unverified_email(
    client, user_factory, password_factory, settings, headless_reverse
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
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
    assert resp.status_code == 401
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
    assert resp.status_code == 200


def test_verify_email_bad_key(
    client, settings, password_factory, user_factory, headless_reverse
):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
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
    assert resp.status_code == 401
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": "bad"},
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert resp.json() == {
        "status": 400,
        "errors": [
            {
                "code": "invalid_or_expired_key",
                "param": "key",
                "message": "Invalid or expired key.",
            }
        ],
    }
