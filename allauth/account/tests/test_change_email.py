from __future__ import absolute_import

import json
from unittest.mock import patch

from django.test.utils import override_settings
from django.urls import reverse

from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import user_email
from allauth.tests import TestCase
from allauth.utils import get_user_model


class ChangeEmailTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username="john", email="john1@example.org")
        self.user.set_password("doe")
        self.user.save()
        self.email_address = EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )
        self.email_address2 = EmailAddress.objects.create(
            user=self.user,
            email="john2@example.org",
            verified=False,
            primary=False,
        )
        self.client.login(username="john", password="doe")

    def test_add(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_add": "", "email": "john3@example.org"},
        )
        EmailAddress.objects.get(
            email="john3@example.org",
            user=self.user,
            verified=False,
            primary=False,
        )
        self.assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")

    def test_ajax_get(self):
        resp = self.client.get(
            reverse("account_email"), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        data = json.loads(resp.content.decode("utf8"))
        assert data["data"] == [
            {
                "id": self.email_address.pk,
                "email": "john1@example.org",
                "primary": True,
                "verified": True,
            },
            {
                "id": self.email_address2.pk,
                "email": "john2@example.org",
                "primary": False,
                "verified": False,
            },
        ]

    def test_ajax_add(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_add": "", "email": "john3@example.org"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = json.loads(resp.content.decode("utf8"))
        self.assertEqual(data["location"], reverse("account_email"))

    def test_ajax_add_invalid(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_add": "", "email": "john3#example.org"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = json.loads(resp.content.decode("utf8"))
        assert "valid" in data["form"]["fields"]["email"]["errors"][0]

    def test_remove_primary(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_remove": "", "email": self.email_address.email},
        )
        EmailAddress.objects.get(pk=self.email_address.pk)
        self.assertTemplateUsed(
            resp, "account/messages/cannot_delete_primary_email.txt"
        )

    def test_ajax_remove_primary(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_remove": "", "email": self.email_address.email},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertTemplateUsed(
            resp, "account/messages/cannot_delete_primary_email.txt"
        )
        data = json.loads(resp.content.decode("utf8"))
        self.assertEqual(data["location"], reverse("account_email"))

    def test_remove_secondary(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_remove": "", "email": self.email_address2.email},
        )
        self.assertRaises(
            EmailAddress.DoesNotExist,
            lambda: EmailAddress.objects.get(pk=self.email_address2.pk),
        )
        self.assertTemplateUsed(resp, "account/messages/email_deleted.txt")

    def test_set_primary_unverified(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_primary": "", "email": self.email_address2.email},
        )
        email_address = EmailAddress.objects.get(pk=self.email_address.pk)
        email_address2 = EmailAddress.objects.get(pk=self.email_address2.pk)
        self.assertFalse(email_address2.primary)
        self.assertTrue(email_address.primary)
        self.assertTemplateUsed(resp, "account/messages/unverified_primary_email.txt")

    def test_set_primary(self):
        email_address2 = EmailAddress.objects.get(pk=self.email_address2.pk)
        email_address2.verified = True
        email_address2.save()
        resp = self.client.post(
            reverse("account_email"),
            {"action_primary": "", "email": self.email_address2.email},
        )
        email_address = EmailAddress.objects.get(pk=self.email_address.pk)
        email_address2 = EmailAddress.objects.get(pk=self.email_address2.pk)
        self.assertFalse(email_address.primary)
        self.assertTrue(email_address2.primary)
        self.assertTemplateUsed(resp, "account/messages/primary_email_set.txt")

    def test_verify(self):
        resp = self.client.post(
            reverse("account_email"),
            {"action_send": "", "email": self.email_address2.email},
        )
        self.assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")

    def test_verify_unknown_email(self):
        assert EmailAddress.objects.filter(user=self.user).count() == 2
        self.client.post(
            reverse("account_email"),
            {"action_send": "", "email": "email@unknown.org"},
        )
        # This unknown email address must not be implicitly added.
        assert EmailAddress.objects.filter(user=self.user).count() == 2

    @override_settings(ACCOUNT_MAX_EMAIL_ADDRESSES=2)
    def test_add_with_two_limiter(self):
        resp = self.client.post(
            reverse("account_email"), {"action_add": "", "email": "john3@example.org"}
        )
        self.assertTemplateNotUsed(resp, "account/messages/email_confirmation_sent.txt")

    @override_settings(ACCOUNT_MAX_EMAIL_ADDRESSES=None)
    def test_add_with_none_limiter(self):
        resp = self.client.post(
            reverse("account_email"), {"action_add": "", "email": "john3@example.org"}
        )
        self.assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")

    @override_settings(ACCOUNT_MAX_EMAIL_ADDRESSES=0)
    def test_add_with_zero_limiter(self):
        resp = self.client.post(
            reverse("account_email"), {"action_add": "", "email": "john3@example.org"}
        )
        self.assertTemplateUsed(resp, "account/messages/email_confirmation_sent.txt")

    def test_set_email_as_primary_doesnt_override_existed_changes_on_the_user(self):
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
        get_user_model().objects.filter(id=user.id).update(
            first_name=updated_first_name
        )

        email.set_as_primary()

        user.refresh_from_db()
        self.assertEqual(user.first_name, updated_first_name)

    @override_settings(ACCOUNT_USER_MODEL_EMAIL_FIELD=None)
    def test_set_email_as_primary_doesnt_override_existed_changes_on_the_user_for_user_model_without_email_field(
        self,
    ):
        self.test_set_email_as_primary_doesnt_override_existed_changes_on_the_user()


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


def test_change_email(user_factory, client, settings):
    settings.ACCOUNT_CHANGE_EMAIL = True
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = True

    user = user_factory(email_verified=True)
    client.force_login(user)
    current_email = EmailAddress.objects.get(user=user)
    resp = client.post(
        reverse("account_email"),
        {"action_add": "", "email": "change-to@this.org"},
    )
    assert resp.status_code == 302
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
