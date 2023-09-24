from __future__ import absolute_import

from django.contrib.auth import get_user_model
from django.core import mail
from django.test.client import RequestFactory
from django.test.utils import override_settings

from allauth.account.forms import ResetPasswordForm
from allauth.tests import TestCase


@override_settings(ACCOUNT_PREVENT_ENUMERATION=False)
class TestCVE2019_19844(TestCase):
    global_request = RequestFactory().get("/")

    def test_user_email_unicode_collision(self):
        User = get_user_model()
        User.objects.create_user("mike123", "mike@example.org", "test123")
        User.objects.create_user("mike456", "mıke@example.org", "test123")
        data = {"email": "mıke@example.org"}
        form = ResetPasswordForm(data)
        self.assertTrue(form.is_valid())
        form.save(self.global_request)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mıke@example.org"])

    def test_user_email_domain_unicode_collision(self):
        User = get_user_model()
        User.objects.create_user("mike123", "mike@ixample.org", "test123")
        User.objects.create_user("mike456", "mike@ıxample.org", "test123")
        data = {"email": "mike@ıxample.org"}
        form = ResetPasswordForm(data)
        self.assertTrue(form.is_valid())
        form.save(self.global_request)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mike@ıxample.org"])

    def test_user_email_unicode_collision_nonexistent(self):
        User = get_user_model()
        User.objects.create_user("mike123", "mike@example.org", "test123")
        data = {"email": "mıke@example.org"}
        form = ResetPasswordForm(data)
        self.assertFalse(form.is_valid())

    def test_user_email_domain_unicode_collision_nonexistent(self):
        User = get_user_model()
        User.objects.create_user("mike123", "mike@ixample.org", "test123")
        data = {"email": "mike@ıxample.org"}
        form = ResetPasswordForm(data)
        self.assertFalse(form.is_valid())
