import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateNotUsed, assertTemplateUsed

from allauth.account.app_settings import LoginMethod
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import user_email


def test_ajax_get(auth_client, user):
    primary = EmailAddress.objects.filter(user=user).first()
    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=False, primary=False
    )
    resp = auth_client.get(
        reverse("account_email"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    data = json.loads(resp.content.decode("utf8"))
    assert data["data"] == [
        {
            "id": primary.pk,
            "email": primary.email,
            "primary": True,
            "verified": True,
        },
        {
            "id": secondary.pk,
            "email": secondary.email,
            "primary": False,
            "verified": False,
        },
    ]


def test_ajax_add(auth_client):
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    data = json.loads(resp.content.decode("utf8"))
    assert data["location"] == reverse("account_email")


def test_ajax_add_invalid(auth_client):
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3#example.org"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    data = json.loads(resp.content.decode("utf8"))
    assert "valid" in data["form"]["fields"]["email"]["errors"][0]


def test_ajax_remove_primary(auth_client, user, settings):
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    resp = auth_client.post(
        reverse("account_email"),
        {"action_remove": "", "email": user.email},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assertTemplateUsed(resp, "account/messages/cannot_delete_primary_email.txt")
    data = json.loads(resp.content.decode("utf8"))
    assert data["location"] == reverse("account_email")


def test_remove_secondary(auth_client, user, settings, mailoutbox):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True

    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=False, primary=False
    )
    resp = auth_client.post(
        reverse("account_email"),
        {"action_remove": "", "email": secondary.email},
    )

    assert not EmailAddress.objects.filter(pk=secondary.pk).exists()
    assertTemplateUsed(resp, "account/messages/email_deleted.txt")
    assert len(mailoutbox) == 1
    assert f"{secondary.email} has been removed" in mailoutbox[0].body


def test_set_primary_unverified(auth_client, user):
    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=False, primary=False
    )
    resp = auth_client.post(
        reverse("account_email"),
        {"action_primary": "", "email": secondary.email},
    )
    primary = EmailAddress.objects.get(email=user.email)
    secondary.refresh_from_db()
    assert not secondary.primary
    assert primary.primary
    assertTemplateUsed(resp, "account/messages/unverified_primary_email.txt")


def test_set_primary(auth_client, user):
    primary = EmailAddress.objects.get(email=user.email)
    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=True, primary=False
    )
    resp = auth_client.post(
        reverse("account_email"),
        {"action_primary": "", "email": secondary.email},
    )
    primary.refresh_from_db()
    secondary.refresh_from_db()
    assert not primary.primary
    assert secondary.primary
    assertTemplateUsed(resp, "account/messages/primary_email_set.txt")


def test_verify(auth_client, user):
    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=False, primary=False
    )
    resp = auth_client.post(
        reverse("account_email"),
        {"action_send": "", "email": secondary.email},
    )
    assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")


def test_verify_unknown_email(auth_client, user):
    auth_client.post(
        reverse("account_email"),
        {"action_send": "", "email": "email@unknown.org"},
    )
    # This unknown email address must not be implicitly added.
    assert EmailAddress.objects.filter(user=user).count() == 1


def test_add_with_two_limiter(auth_client, user, settings):
    EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=False, primary=False
    )
    settings.ACCOUNT_MAX_EMAIL_ADDRESSES = 2
    resp = auth_client.post(
        reverse("account_email"), {"action_add": "", "email": "john3@example.org"}
    )
    assertTemplateNotUsed(resp, "account/messages/email_confirmation_sent.txt")


def test_add_with_none_limiter(auth_client, settings):
    settings.ACCOUNT_MAX_EMAIL_ADDRESSES = None
    resp = auth_client.post(
        reverse("account_email"), {"action_add": "", "email": "john3@example.org"}
    )
    assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")


def test_add_with_zero_limiter(auth_client, settings):
    settings.ACCOUNT_MAX_EMAIL_ADDRESSES = 0
    resp = auth_client.post(
        reverse("account_email"), {"action_add": "", "email": "john3@example.org"}
    )
    assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")


@pytest.mark.parametrize("has_email_field", [True, False])
def test_set_email_as_primary_doesnt_override_existing_changes_on_the_user(
    db, has_email_field, settings
):
    if not has_email_field:
        settings.ACCOUNT_USER_MODEL_EMAIL_FIELD = None
    user = get_user_model().objects.create(
        username="@raymond.penners", first_name="Before Update"
    )
    email = EmailAddress.objects.create(
        user=user,
        email="raymond.penners@example.com",
        primary=True,
        verified=True,
    )
    updated_first_name = "Updated"
    get_user_model().objects.filter(id=user.id).update(first_name=updated_first_name)

    email.set_as_primary()

    user.refresh_from_db()
    assert user.first_name == updated_first_name


def test_delete_email_changes_user_email(user_factory, client, email_factory):
    user = user_factory(email_verified=False)
    client.force_login(user)
    first_email = EmailAddress.objects.get(user=user)
    first_email.primary = False
    first_email.save()
    # other_unverified_email
    EmailAddress.objects.create(
        user=user, email=email_factory(), verified=False, primary=False
    )
    other_verified_email = EmailAddress.objects.create(
        user=user, email=email_factory(), verified=True, primary=False
    )
    assert user_email(user) == first_email.email
    resp = client.post(
        reverse("account_email"),
        {"action_remove": "", "email": first_email.email},
    )
    assert resp.status_code == 302
    user.refresh_from_db()
    assert user_email(user) == other_verified_email.email


def test_delete_email_wipes_user_email(user_factory, client):
    user = user_factory(email_verified=False)
    client.force_login(user)
    first_email = EmailAddress.objects.get(user=user)
    first_email.primary = False
    first_email.save()
    assert user_email(user) == first_email.email
    resp = client.post(
        reverse("account_email"),
        {"action_remove": "", "email": first_email.email},
    )
    assert resp.status_code == 302
    user.refresh_from_db()
    assert user_email(user) == ""


def test_change_email(user_factory, client, settings, mailoutbox):
    settings.ACCOUNT_CHANGE_EMAIL = True
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True

    user = user_factory(email_verified=True)
    client.force_login(user)
    current_email = EmailAddress.objects.get(user=user)
    resp = client.post(
        reverse("account_email"),
        {"action_add": "", "email": "change-to@this.org"},
    )
    assert resp.status_code == 302
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "[example.com] Please Confirm Your Email Address"
    new_email = EmailAddress.objects.get(email="change-to@this.org")
    key = EmailConfirmationHMAC(new_email).key
    with patch("allauth.account.signals.email_changed.send") as email_changed_mock:
        resp = client.post(reverse("account_confirm_email", args=[key]))
    assert resp.status_code == 302
    assert not EmailAddress.objects.filter(pk=current_email.pk).exists()
    assert EmailAddress.objects.filter(user=user).count() == 1
    new_email.refresh_from_db()
    assert new_email.verified
    assert new_email.primary
    assert email_changed_mock.called
    assert len(mailoutbox) == 2
    assert mailoutbox[1].subject == "[example.com] Email Changed"
    assert mailoutbox[1].to == [user.email]


def test_add(auth_client, user, settings):
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
    )
    EmailAddress.objects.get(
        email="john3@example.org",
        user=user,
        verified=False,
        primary=False,
    )
    assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")


def test_add_with_reauthentication(auth_client, user, user_password, settings):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
    )
    assert not EmailAddress.objects.filter(email="john3@example.org").exists()
    assert resp.status_code == 302
    assert (
        resp["location"]
        == reverse("account_reauthenticate") + "?next=%2Faccounts%2Femail%2F"
    )
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert EmailAddress.objects.filter(email="john3@example.org").exists()
    assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_email")


@pytest.mark.parametrize(
    "prevent_enumeration",
    [
        False,
        True,
        "strict",
    ],
)
def test_add_not_allowed(
    auth_client, user, settings, user_factory, prevent_enumeration
):
    settings.ACCOUNT_PREVENT_ENUMERATION = prevent_enumeration
    email = "inuse@byotheruser.com"
    user_factory(email=email)
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": email},
    )
    if prevent_enumeration:
        assert resp.status_code == 302
        email_address = EmailAddress.objects.get(
            email=email,
            user=user,
            verified=False,
            primary=False,
        )
        assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")
        key = EmailConfirmationHMAC(email_address).key
        resp = auth_client.post(reverse("account_confirm_email", args=[key]))
        assertTemplateUsed(resp, "account/messages/email_confirmation_failed.txt")
        assert resp.status_code == 302
        email_address.refresh_from_db()
        assert not email_address.verified
    else:
        assert resp.status_code == 200
        assert resp.context["form"].errors == {
            "email": ["A user is already registered with this email address."]
        }


@pytest.mark.parametrize(
    "login_methods,primary_email,secondary_emails,delete_email,success",
    [
        ({LoginMethod.EMAIL}, "pri@ma.il", ["sec@ma.il"], "pri@ma.il", False),
        ({LoginMethod.EMAIL}, "pri@ma.il", ["sec@ma.il"], "sec@ma.il", True),
        ({LoginMethod.EMAIL}, "pri@ma.il", [], "pri@ma.il", False),
        ({LoginMethod.USERNAME}, "pri@ma.il", ["sec@ma.il"], "pri@ma.il", False),
        ({LoginMethod.USERNAME}, "pri@ma.il", ["sec@ma.il"], "sec@ma.il", True),
        ({LoginMethod.USERNAME}, "pri@ma.il", [], "pri@ma.il", True),
        (
            {LoginMethod.USERNAME, LoginMethod.EMAIL},
            "pri@ma.il",
            ["sec@ma.il"],
            "pri@ma.il",
            False,
        ),
        (
            {LoginMethod.USERNAME, LoginMethod.EMAIL},
            "pri@ma.il",
            ["sec@ma.il"],
            "sec@ma.il",
            True,
        ),
        ({LoginMethod.USERNAME, LoginMethod.EMAIL}, "pri@ma.il", [], "pri@ma.il", True),
    ],
)
def test_remove_email(
    client,
    settings,
    user_factory,
    primary_email,
    secondary_emails,
    delete_email,
    login_methods,
    success,
):
    settings.ACCOUNT_LOGIN_METHODS = login_methods
    user = user_factory(email=primary_email)
    EmailAddress.objects.bulk_create(
        [
            EmailAddress(user=user, email=email, primary=False, verified=False)
            for email in secondary_emails
        ]
    )
    client.force_login(user)
    resp = client.post(
        reverse("account_email"),
        {"action_remove": "", "email": delete_email},
    )
    assert EmailAddress.objects.filter(email=delete_email).exists() == (not success)
    if not success:
        assertTemplateUsed(resp, "account/messages/cannot_delete_primary_email.txt")


@pytest.mark.parametrize(
    "email,did_look_up",
    [
        ("valid@email.org", True),
        ("not-an-email", False),
    ],
)
def test_dont_lookup_invalid_email(auth_client, email, did_look_up):
    with patch("allauth.account.views.EmailAddress.objects.get_for_user") as gfu_mock:
        gfu_mock.side_effect = EmailAddress.DoesNotExist
        auth_client.post(
            reverse("account_email"),
            {"action_remove": "", "email": email},
        )
        assert gfu_mock.called == did_look_up


def test_add_requires_reauthentication(settings, auth_client):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True
    resp = auth_client.post(
        reverse("account_email"),
        {"action_add": "", "email": "john3@example.org"},
    )
    assert not EmailAddress.objects.filter(email="john3@example.org").exists()
    assert resp["location"].startswith(reverse("account_reauthenticate"))


def test_remove_requires_reauthentication(auth_client, user, settings):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True
    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=False, primary=False
    )
    resp = auth_client.post(
        reverse("account_email"),
        {"action_remove": "", "email": secondary.email},
    )
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    assert EmailAddress.objects.filter(pk=secondary.pk).exists()


def test_set_primary_requires_reauthentication(auth_client, user, settings):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True
    primary = EmailAddress.objects.get(email=user.email)
    secondary = EmailAddress.objects.create(
        email="secondary@email.org", user=user, verified=True, primary=False
    )
    resp = auth_client.post(
        reverse("account_email"),
        {"action_primary": "", "email": secondary.email},
    )
    assert resp["location"].startswith(reverse("account_reauthenticate"))
    primary.refresh_from_db()
    secondary.refresh_from_db()
    assert primary.primary
    assert not secondary.primary
