from __future__ import absolute_import

from datetime import timedelta

from django.conf import settings
from django.core import mail
from django.http import HttpResponseRedirect
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.timezone import now

from allauth.account import app_settings
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC,
)
from allauth.account.signals import user_logged_in
from allauth.account.utils import user_pk_to_url_str
from allauth.tests import Mock, TestCase, patch
from allauth.utils import get_user_model

from .test_models import UUIDUser


@override_settings(
    ACCOUNT_DEFAULT_HTTP_PROTOCOL="https",
    ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.MANDATORY,
    ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    ACCOUNT_EMAIL_SUBJECT_PREFIX=None,
    LOGIN_REDIRECT_URL="/accounts/profile/",
    ACCOUNT_SIGNUP_REDIRECT_URL="/accounts/welcome/",
    ACCOUNT_ADAPTER="allauth.account.adapter.DefaultAccountAdapter",
    ACCOUNT_USERNAME_REQUIRED=True,
)
class ConfirmationViewTests(TestCase):
    def _create_user(self, username="john", password="doe", **kwargs):
        user = get_user_model().objects.create(
            username=username, is_active=True, **kwargs
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=True,
        ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION=True,
    )
    def test_login_on_confirm(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user, email="a@b.com", verified=False, primary=True
        )
        key = EmailConfirmationHMAC(email).key

        receiver_mock = Mock()  # we've logged if signal was called
        user_logged_in.connect(receiver_mock)

        # fake post-signup account_user stash
        session = self.client.session
        session["account_user"] = user_pk_to_url_str(user)
        session.save()

        resp = self.client.post(reverse("account_confirm_email", args=[key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertTrue(email.verified)

        receiver_mock.assert_called_once_with(
            sender=get_user_model(),
            request=resp.wsgi_request,
            response=resp,
            user=get_user_model().objects.get(username="john"),
            signal=user_logged_in,
        )

        user_logged_in.disconnect(receiver_mock)

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=True,
        ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION=True,
    )
    @patch("allauth.account.views.perform_login")
    @patch("allauth.account.utils.get_user_model", return_value=UUIDUser)
    def test_login_on_confirm_uuid_user(self, mocked_gum, mock_perform_login):
        user = UUIDUser(is_active=True, email="john@example.com", username="john")

        # fake post-signup account_user stash
        session = self.client.session
        session["account_user"] = user_pk_to_url_str(user)
        session.save()

        # fake email and email confirmation to avoid swappable model hell
        email = Mock(verified=False, user=user)
        key = "mockkey"
        confirmation = Mock(autospec=EmailConfirmationHMAC, key=key)
        confirmation.email_address = email
        confirmation.from_key.return_value = confirmation
        mock_perform_login.return_value = HttpResponseRedirect(redirect_to="/")

        with patch("allauth.account.views.EmailConfirmationHMAC", confirmation):
            self.client.post(reverse("account_confirm_email", args=[key]))

        assert mock_perform_login.called

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=False,
    )
    def test_email_verification_failed(self):
        verified_user = get_user_model().objects.create(username="foobar")
        unverified_user = get_user_model().objects.create(username="foobar2")
        EmailAddress.objects.create(
            user=verified_user,
            email="foo@bar.org",
            verified=True,
            primary=True,
        )
        email_address = EmailAddress.objects.create(
            user=unverified_user,
            email="foo@bar.org",
            verified=False,
            primary=False,
        )
        confirmation = EmailConfirmation.objects.create(
            email_address=email_address,
            key="dummy",
            sent=now(),
        )
        c = Client()
        resp = c.post(reverse("account_confirm_email", args=[confirmation.key]))
        self.assertTemplateUsed(resp, "account/messages/email_confirmation_failed.txt")

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=False, ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN=10
    )
    def test_email_verification_mandatory(self):
        c = Client()
        # Signup
        resp = c.post(
            reverse("account_signup"),
            {
                "username": "johndoe",
                "email": "john@example.com",
                "password1": "johndoe",
                "password2": "johndoe",
            },
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mail.outbox[0].to, ["john@example.com"])
        self.assertGreater(mail.outbox[0].body.find("https://"), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTemplateUsed(
            resp,
            "account/verification_sent.%s" % app_settings.TEMPLATE_EXTENSION,
        )
        # Attempt to login, unverified
        for attempt in [1, 2]:
            resp = c.post(
                reverse("account_login"),
                {"login": "johndoe", "password": "johndoe"},
                follow=True,
            )
            # is_active is controlled by the admin to manually disable
            # users. I don't want this flag to flip automatically whenever
            # users verify their email addresses.
            self.assertTrue(
                get_user_model()
                .objects.filter(username="johndoe", is_active=True)
                .exists()
            )

            self.assertTemplateUsed(
                resp,
                "account/verification_sent." + app_settings.TEMPLATE_EXTENSION,
            )
            # Attempt 1: no mail is sent due to cool-down ,
            # but there was already a mail in the outbox.
            self.assertEqual(len(mail.outbox), attempt)
            self.assertEqual(
                EmailConfirmation.objects.filter(
                    email_address__email="john@example.com"
                ).count(),
                attempt,
            )
            # Wait for cooldown
            EmailConfirmation.objects.update(sent=now() - timedelta(days=1))
        # Verify, and re-attempt to login.
        confirmation = EmailConfirmation.objects.filter(
            email_address__user__username="johndoe"
        )[:1].get()
        resp = c.get(reverse("account_confirm_email", args=[confirmation.key]))
        self.assertTemplateUsed(
            resp, "account/email_confirm.%s" % app_settings.TEMPLATE_EXTENSION
        )
        c.post(reverse("account_confirm_email", args=[confirmation.key]))
        resp = c.post(
            reverse("account_login"),
            {"login": "johndoe", "password": "johndoe"},
        )
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.OPTIONAL,
        ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE=False,
    )
    def test_optional_email_verification(self):
        c = Client()
        # Signup
        c.get(reverse("account_signup"))
        resp = c.post(
            reverse("account_signup"),
            {
                "username": "johndoe",
                "email": "john@example.com",
                "password1": "johndoe",
            },
        )
        # Logged in
        self.assertRedirects(
            resp, settings.ACCOUNT_SIGNUP_REDIRECT_URL, fetch_redirect_response=False
        )
        self.assertEqual(mail.outbox[0].to, ["john@example.com"])
        self.assertEqual(len(mail.outbox), 1)
        # Logout & login again
        c.logout()
        # Wait for cooldown
        EmailConfirmation.objects.update(sent=now() - timedelta(days=1))
        # Signup
        resp = c.post(
            reverse("account_login"),
            {"login": "johndoe", "password": "johndoe"},
        )
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )
        self.assertEqual(mail.outbox[0].to, ["john@example.com"])
        # There was an issue that we sent out email confirmation mails
        # on each login in case of optional verification. Make sure
        # this is not the case:
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=True)
    def test_email_confirmation_hmac_falls_back(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user, email="a@b.com", verified=False, primary=True
        )
        confirmation = EmailConfirmation.create(email)
        confirmation.sent = now()
        confirmation.save()
        self.client.post(reverse("account_confirm_email", args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertTrue(email.verified)

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=True)
    def test_email_confirmation_hmac(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user, email="a@b.com", verified=False, primary=True
        )
        confirmation = EmailConfirmationHMAC(email)
        request = RequestFactory().get("/")
        confirmation.send(request=request)
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(reverse("account_confirm_email", args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertTrue(email.verified)

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=True,
        ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS=0,
    )
    def test_email_confirmation_hmac_timeout(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user, email="a@b.com", verified=False, primary=True
        )
        confirmation = EmailConfirmationHMAC(email)
        request = RequestFactory().get("/")
        confirmation.send(request=request)
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(reverse("account_confirm_email", args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertFalse(email.verified)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL
    )
    def test_confirm_email_with_another_user_logged_in(self):
        """Test the email confirmation view. If User B clicks on an email
        verification link while logged in as User A, ensure User A gets
        logged out."""
        user = get_user_model().objects.create_user(
            username="john", email="john@example.org", password="doe"
        )
        self.client.force_login(user)
        self.client.post(
            reverse("account_email"), {"email": user.email, "action_send": ""}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.client.logout()

        body = mail.outbox[0].body
        self.assertGreater(body.find("https://"), 0)

        user2 = self._create_user(username="john2", email="john2@example.com")
        EmailAddress.objects.create(
            user=user2, email=user2.email, primary=True, verified=True
        )
        resp = self.client.post(
            reverse("account_login"),
            {
                "login": user2.email,
                "password": "doe",
            },
        )
        self.assertEqual(user2, resp.context["user"])

        url = body[body.find("/confirm-email/") :].split()[0]
        resp = self.client.post(url)

        self.assertTemplateUsed(resp, "account/messages/logged_out.txt")
        self.assertTemplateUsed(resp, "account/messages/email_confirmed.txt")

        self.assertRedirects(resp, settings.LOGIN_URL, fetch_redirect_response=False)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL
    )
    def test_confirm_email_with_same_user_logged_in(self):
        """Test the email confirmation view. If User A clicks on an email
        verification link while logged in, ensure the user
        stayed logged in."""
        user = get_user_model().objects.create_user(
            username="john", email="john@example.org", password="doe"
        )
        self.client.force_login(user)
        self.client.post(
            reverse("account_email"), {"email": user.email, "action_send": ""}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])

        body = mail.outbox[0].body
        self.assertGreater(body.find("https://"), 0)

        url = body[body.find("/confirm-email/") :].split()[0]
        resp = self.client.post(url)

        self.assertTemplateNotUsed(resp, "account/messages/logged_out.txt")
        self.assertTemplateUsed(resp, "account/messages/email_confirmed.txt")

        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

        self.assertEqual(user, resp.wsgi_request.user)
