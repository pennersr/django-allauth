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
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1
    assert not EmailAddress.objects.filter(pk=addr.pk).exists()


def test_add_email(auth_client, user, email_factory, headless_reverse):
    new_email = email_factory()
    resp = auth_client.post(
        headless_reverse("headless:account:manage_email"),
        data={"email": new_email},
        content_type="application/json",
    )
    assert resp.status_code == 200
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
    assert resp.status_code == 200
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
    assert resp.status_code == 200
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
        expected_status = 200 if attempt == 0 else 429
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
        assert resp.status_code == 403 if attempt else 200
        assert len(mailoutbox) == 1
