from http import HTTPStatus

from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress


def test_list_email(auth_client, user, headless_reverse):
    resp = auth_client.get(
        headless_reverse("headless:account:manage_email"),
    )
    assert len(resp.json()["data"]) == 1


def test_remove_email(auth_client, user, email_factory, headless_reverse):
    addr = EmailAddress.objects.create(email=email_factory(), user=user)
    assert EmailAddress.objects.filter(user=user).count() == 2
    resp = auth_client.delete(
        headless_reverse("headless:account:manage_email"),
        data={"email": addr.email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()["data"]) == 1
    assert not EmailAddress.objects.filter(pk=addr.pk).exists()


def test_add_email(auth_client, user, email_factory, headless_reverse):
    new_email = email_factory()
    resp = auth_client.post(
        headless_reverse("headless:account:manage_email"),
        data={"email": new_email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()["data"]) == 2
    assert EmailAddress.objects.filter(email=new_email, verified=False).exists()


def test_change_primary(auth_client, user, email_factory, headless_reverse):
    addr = EmailAddress.objects.create(
        email=email_factory(), user=user, verified=True, primary=False
    )
    resp = auth_client.patch(
        headless_reverse("headless:account:manage_email"),
        data={"email": addr.email, "primary": True},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()["data"]) == 2
    assert EmailAddress.objects.filter(pk=addr.pk, primary=True).exists()


def test_resend_verification(
    auth_client, user, email_factory, headless_reverse, mailoutbox
):
    addr = EmailAddress.objects.create(email=email_factory(), user=user, verified=False)
    resp = auth_client.put(
        headless_reverse("headless:account:manage_email"),
        data={"email": addr.email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(mailoutbox) == 1


def test_email_rate_limit(
    auth_client, user, email_factory, headless_reverse, settings, enable_cache
):
    settings.ACCOUNT_RATE_LIMITS = {"manage_email": "1/m/ip"}
    for attempt in range(2):
        new_email = email_factory()
        resp = auth_client.post(
            headless_reverse("headless:account:manage_email"),
            data={"email": new_email},
            content_type="application/json",
        )
        expected_status = (
            HTTPStatus.OK if attempt == 0 else HTTPStatus.TOO_MANY_REQUESTS
        )
        assert resp.status_code == expected_status
        assert resp.json()["status"] == expected_status


def test_resend_verification_rate_limit(
    auth_client,
    user,
    email_factory,
    headless_reverse,
    settings,
    enable_cache,
    mailoutbox,
):
    settings.ACCOUNT_RATE_LIMITS = {"confirm_email": "1/m/ip"}
    for attempt in range(2):
        addr = EmailAddress.objects.create(
            email=email_factory(), user=user, verified=False
        )
        resp = auth_client.put(
            headless_reverse("headless:account:manage_email"),
            data={"email": addr.email},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.FORBIDDEN if attempt else HTTPStatus.OK
        assert len(mailoutbox) == 1


def test_change_email_to_conflicting(
    settings,
    auth_client,
    user,
    email_factory,
    headless_reverse,
    user_factory,
    get_last_email_verification_code,
    mailoutbox,
):
    other_user = user_factory(email="taken@conflict.org")
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_CHANGE_EMAIL = True
    resp = auth_client.post(
        headless_reverse("headless:account:manage_email"),
        data={"email": other_user.email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()["data"]) == 2
    assert EmailAddress.objects.filter(user=user).count() == 1
    code = get_last_email_verification_code(auth_client, mailoutbox)
    resp = auth_client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "status": HTTPStatus.BAD_REQUEST,
        "errors": [
            {
                "message": "A user is already registered with this email address.",
                "code": "email_taken",
                "param": "key",
            }
        ],
    }


def test_change_email_by_code(
    settings,
    auth_client,
    user,
    email_factory,
    headless_reverse,
    user_factory,
    get_last_email_verification_code,
    mailoutbox,
):
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_CHANGE_EMAIL = True
    new_email = email_factory()
    resp = auth_client.post(
        headless_reverse("headless:account:manage_email"),
        data={"email": new_email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()["data"]) == 2
    assert EmailAddress.objects.filter(user=user).count() == 1
    code = get_last_email_verification_code(auth_client, mailoutbox)
    resp = auth_client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert EmailAddress.objects.filter(user=user).count() == 1
    assert EmailAddress.objects.filter(user=user, email=new_email).exists()


def test_change_email_at_signup(
    settings,
    client,
    user,
    email_factory,
    headless_reverse,
    user_factory,
    get_last_email_verification_code,
    mailoutbox,
    password_factory,
):
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.ACCOUNT_CHANGE_EMAIL = True
    settings.ACCOUNT_EMAIL_VERIFICATION_SUPPORTS_CHANGE = True
    email = email_factory()
    resp = client.post(
        headless_reverse("headless:account:signup"),
        data={
            "username": "wizard",
            "email": email,
            "password": password_factory(),
        },
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    user = get_user_model().objects.last()
    assert EmailAddress.objects.filter(user=user).count() == 1
    assert EmailAddress.objects.filter(user=user, email=email, verified=False).exists()

    new_email = email_factory()
    resp = client.post(
        headless_reverse("headless:account:manage_email"),
        data={"email": new_email},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert len(resp.json()["data"]) == 1
    assert EmailAddress.objects.filter(user=user).count() == 1
    assert EmailAddress.objects.filter(
        user=user, email=new_email, verified=False
    ).exists()

    code = get_last_email_verification_code(client, mailoutbox)
    resp = client.post(
        headless_reverse("headless:account:verify_email"),
        data={"key": code},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    assert EmailAddress.objects.filter(user=user).count() == 1
    assert EmailAddress.objects.filter(
        user=user, email=new_email, verified=True
    ).exists()
