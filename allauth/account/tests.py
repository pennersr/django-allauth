from __future__ import absolute_import

import json
import uuid
from datetime import timedelta

from django import forms
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.contrib.sites.models import Site
from django.core import mail, validators
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseRedirect
from django.template import Context, Template
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.timezone import now

from allauth.account.forms import BaseSignupForm, ResetPasswordForm, SignupForm
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC,
)
from allauth.tests import Mock, TestCase, patch
from allauth.utils import get_user_model, get_username_max_length

from . import app_settings
from .adapter import get_adapter
from .auth_backends import AuthenticationBackend
from .signals import user_logged_in, user_logged_out
from .utils import (
    filter_users_by_username,
    url_str_to_user_pk,
    user_pk_to_url_str,
    user_username,
)


test_username_validators = [
    validators.RegexValidator(regex=r"^[a-c]+$", message="not abc", flags=0)
]


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
class AccountTests(TestCase):
    def setUp(self):
        if "allauth.socialaccount" in settings.INSTALLED_APPS:
            # Otherwise ImproperlyConfigured exceptions may occur
            from ..socialaccount.models import SocialApp

            sa = SocialApp.objects.create(name="testfb", provider="facebook")
            sa.sites.add(Site.objects.get_current())

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL
    )
    def test_username_containing_at(self):
        user = get_user_model().objects.create(username="@raymond.penners")
        user.set_password("psst")
        user.save()
        EmailAddress.objects.create(
            user=user,
            email="raymond.penners@example.com",
            primary=True,
            verified=True,
        )
        resp = self.client.post(
            reverse("account_login"),
            {"login": "@raymond.penners", "password": "psst"},
        )
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    def test_signup_same_email_verified_externally(self):
        user = self._test_signup_email_verified_externally(
            "john@example.com", "john@example.com"
        )
        self.assertEqual(EmailAddress.objects.filter(user=user).count(), 1)
        EmailAddress.objects.get(
            verified=True, email="john@example.com", user=user, primary=True
        )

    def test_signup_other_email_verified_externally(self):
        """
        John is invited on john@example.org, but signs up via john@example.com.
        E-mail verification is by-passed, their home e-mail address is
        used as a secondary.
        """
        user = self._test_signup_email_verified_externally(
            "john@example.com", "john@example.org"
        )
        self.assertEqual(EmailAddress.objects.filter(user=user).count(), 2)
        EmailAddress.objects.get(
            verified=False, email="john@example.com", user=user, primary=False
        )
        EmailAddress.objects.get(
            verified=True, email="john@example.org", user=user, primary=True
        )

    def _test_signup_email_verified_externally(self, signup_email, verified_email):
        username = "johndoe"
        request = RequestFactory().post(
            reverse("account_signup"),
            {
                "username": username,
                "email": signup_email,
                "password1": "johndoe",
                "password2": "johndoe",
            },
        )
        # Fake stash_verified_email
        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        request.user = AnonymousUser()
        request.session["account_verified_email"] = verified_email
        from .views import signup

        resp = signup(request)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(
            resp["location"], get_adapter().get_signup_redirect_url(request)
        )
        self.assertEqual(len(mail.outbox), 0)
        return get_user_model().objects.get(username=username)

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE=True,
    )
    def test_signup_password_twice_form_error(self):
        resp = self.client.post(
            reverse("account_signup"),
            data={
                "username": "johndoe",
                "email": "john@example.org",
                "password1": "johndoe",
                "password2": "janedoe",
            },
        )
        self.assertFormError(
            resp,
            "form",
            "password2",
            "You must type the same password each time.",
        )

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True, ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE=True
    )
    def test_signup_email_twice(self):
        request = RequestFactory().post(
            reverse("account_signup"),
            {
                "username": "johndoe",
                "email": "john@example.org",
                "email2": "john@example.org",
                "password1": "johndoe",
                "password2": "johndoe",
            },
        )
        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware

        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        request.user = AnonymousUser()
        from .views import signup

        signup(request)
        user = get_user_model().objects.get(username="johndoe")
        self.assertEqual(user.email, "john@example.org")

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

    def _create_user_and_login(self, usable_password=True):
        password = "doe" if usable_password else False
        user = self._create_user(password=password)
        self.client.force_login(user)
        return user

    def test_redirect_when_authenticated(self):
        self._create_user_and_login()
        c = self.client
        resp = c.get(reverse("account_login"))
        self.assertRedirects(resp, "/accounts/profile/", fetch_redirect_response=False)

    def test_password_reset_get(self):
        resp = self.client.get(reverse("account_reset_password"))
        self.assertTemplateUsed(resp, "account/password_reset.html")

    def test_password_set_redirect(self):
        resp = self._password_set_or_change_redirect("account_set_password", True)
        self.assertRedirects(
            resp,
            reverse("account_change_password"),
            fetch_redirect_response=False,
        )

    def test_set_password_not_allowed(self):
        user = self._create_user_and_login(True)
        pwd = "!*123i1uwn12W23"
        self.assertFalse(user.check_password(pwd))
        resp = self.client.post(
            reverse("account_set_password"),
            data={"password1": pwd, "password2": pwd},
        )
        user.refresh_from_db()
        self.assertFalse(user.check_password(pwd))
        self.assertTrue(user.has_usable_password())
        self.assertEqual(resp.status_code, 302)

    def test_password_change_no_redirect(self):
        resp = self._password_set_or_change_redirect("account_change_password", True)
        self.assertEqual(resp.status_code, 200)

    def test_password_set_no_redirect(self):
        resp = self._password_set_or_change_redirect("account_set_password", False)
        self.assertEqual(resp.status_code, 200)

    def test_password_change_redirect(self):
        resp = self._password_set_or_change_redirect("account_change_password", False)
        self.assertRedirects(
            resp,
            reverse("account_set_password"),
            fetch_redirect_response=False,
        )

    def _password_set_or_change_redirect(self, urlname, usable_password):
        self._create_user_and_login(usable_password)
        return self.client.get(reverse(urlname))

    def test_ajax_password_change(self):
        self._create_user_and_login()
        resp = self.client.post(
            reverse("account_change_password"),
            data={
                "oldpassword": "doe",
                "password1": "AbCdEf!123",
                "password2": "AbCdEf!123456",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp["content-type"], "application/json")
        data = json.loads(resp.content.decode("utf8"))
        assert "same password" in data["form"]["fields"]["password2"]["errors"][0]

    def test_password_forgotten_username_hint(self):
        user = self._request_new_password()
        body = mail.outbox[0].body
        assert user.username in body

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL
    )
    def test_password_forgotten_no_username_hint(self):
        user = self._request_new_password()
        body = mail.outbox[0].body
        assert user.username not in body

    def _request_new_password(self):
        user = get_user_model().objects.create(
            username="john", email="john@example.org", is_active=True
        )
        user.set_password("doe")
        user.save()
        self.client.post(
            reverse("account_reset_password"),
            data={"email": "john@example.org"},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["john@example.org"])
        return user

    def test_password_reset_flow_with_empty_session(self):
        """
        Test the password reset flow when the session is empty:
        requesting a new password, receiving the reset link via email,
        following the link, getting redirected to the
        new link (without the token)
        Copying the link and using it in a DIFFERENT client (Browser/Device).
        """
        # Request new password
        self._request_new_password()
        body = mail.outbox[0].body
        self.assertGreater(body.find("https://"), 0)

        # Extract URL for `password_reset_from_key` view
        url = body[body.find("/password/reset/") :].split()[0]
        resp = self.client.get(url)

        reset_pass_url = resp.url

        # Accesing the url via a different session
        resp = self.client_class().get(reset_pass_url)

        # We should receive the token_fail context_data
        self.assertTemplateUsed(
            resp,
            "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION,
        )

        self.assertTrue(resp.context_data["token_fail"])

    def test_password_reset_flow(self):
        """
        Tests the password reset flow: requesting a new password,
        receiving the reset link via email and finally resetting the
        password to a new value.
        """
        # Request new password
        user = self._request_new_password()
        body = mail.outbox[0].body
        self.assertGreater(body.find("https://"), 0)

        # Extract URL for `password_reset_from_key` view and access it
        url = body[body.find("/password/reset/") :].split()[0]
        resp = self.client.get(url)
        # Follow the redirect the actual password reset page with the key
        # hidden.
        url = resp.url
        resp = self.client.get(url)
        self.assertTemplateUsed(
            resp,
            "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION,
        )
        self.assertFalse("token_fail" in resp.context_data)

        # Reset the password
        resp = self.client.post(
            url, {"password1": "newpass123", "password2": "newpass123"}
        )
        self.assertRedirects(resp, reverse("account_reset_password_from_key_done"))

        # Check the new password is in effect
        user = get_user_model().objects.get(pk=user.pk)
        self.assertTrue(user.check_password("newpass123"))

        # Trying to reset the password against the same URL (or any other
        # invalid/obsolete URL) returns a bad token response
        resp = self.client.post(
            url, {"password1": "newpass123", "password2": "newpass123"}
        )
        self.assertTemplateUsed(
            resp,
            "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION,
        )
        self.assertTrue(resp.context_data["token_fail"])

        # Same should happen when accessing the page directly
        response = self.client.get(url)
        self.assertTemplateUsed(
            response,
            "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION,
        )
        self.assertTrue(response.context_data["token_fail"])

        # When in XHR views, it should respond with a 400 bad request
        # code, and the response body should contain the JSON-encoded
        # error from the adapter
        response = self.client.post(
            url,
            {"password1": "newpass123", "password2": "newpass123"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode("utf8"))
        assert "invalid" in data["form"]["errors"][0]

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL
    )
    def test_password_reset_flow_with_another_user_logged_in(self):
        """
        Tests the password reset flow: if User B requested a password
        reset earlier and now User A is logged in, User B now clicks on
        the link, ensure User A is logged out before continuing.
        """
        # Request new password
        self._request_new_password()
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

        # Extract URL for `password_reset_from_key` view and access it
        url = body[body.find("/password/reset/") :].split()[0]
        resp = self.client.get(url)
        # Follow the redirect the actual password reset page with the key
        # hidden.
        url = resp.url
        resp = self.client.get(url)
        self.assertTemplateUsed(
            resp, "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION
        )
        self.assertFalse("token_fail" in resp.context_data)

        # Reset the password
        resp = self.client.post(
            url, {"password1": "newpass123", "password2": "newpass123"}, follow=True
        )
        self.assertRedirects(resp, reverse("account_reset_password_from_key_done"))

        self.assertNotEqual(user2, resp.context["user"])
        self.assertEqual(AnonymousUser(), resp.context["user"])

    def test_password_reset_flow_with_email_changed(self):
        """
        Test that the password reset token is invalidated if
        the user email address was changed.
        """
        user = self._request_new_password()
        body = mail.outbox[0].body
        self.assertGreater(body.find("https://"), 0)
        EmailAddress.objects.create(user=user, email="other@email.org")
        # Extract URL for `password_reset_from_key` view
        url = body[body.find("/password/reset/") :].split()[0]
        resp = self.client.get(url)
        self.assertTemplateUsed(
            resp,
            "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION,
        )
        self.assertTrue("token_fail" in resp.context_data)

    @override_settings(ACCOUNT_LOGIN_ON_PASSWORD_RESET=True)
    def test_password_reset_ACCOUNT_LOGIN_ON_PASSWORD_RESET(self):
        user = self._request_new_password()
        body = mail.outbox[0].body
        url = body[body.find("/password/reset/") :].split()[0]
        resp = self.client.get(url)
        # Follow the redirect the actual password reset page with the key
        # hidden.
        resp = self.client.post(
            resp.url, {"password1": "newpass123", "password2": "newpass123"}
        )
        self.assertTrue(user.is_authenticated)
        # EmailVerificationMethod.MANDATORY sends us to the confirm-email page
        self.assertRedirects(resp, "/confirm-email/")

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=False)
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
            # users verify their email adresses.
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

    def test_email_escaping(self):
        site = Site.objects.get_current()
        site.name = '<enc&"test>'
        site.save()
        u = get_user_model().objects.create(username="test", email="user@example.com")
        request = RequestFactory().get("/")
        EmailAddress.objects.add_email(request, u, u.email, confirm=True)
        self.assertTrue(mail.outbox[0].subject[1:].startswith(site.name))

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.OPTIONAL
    )
    def test_login_unverified_account_optional(self):
        """Tests login behavior when email verification is optional."""
        user = get_user_model().objects.create(username="john")
        user.set_password("doe")
        user.save()
        EmailAddress.objects.create(
            user=user, email="user@example.com", primary=True, verified=False
        )
        resp = self.client.post(
            reverse("account_login"), {"login": "john", "password": "doe"}
        )
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.OPTIONAL,
        ACCOUNT_LOGIN_ATTEMPTS_LIMIT=3,
    )
    def test_login_failed_attempts_exceeded(self):
        user = get_user_model().objects.create(username="john")
        user.set_password("doe")
        user.save()
        EmailAddress.objects.create(
            user=user, email="user@example.com", primary=True, verified=False
        )
        for i in range(5):
            is_valid_attempt = i == 4
            is_locked = i >= 3
            resp = self.client.post(
                reverse("account_login"),
                {
                    "login": ["john", "John", "JOHN", "JOhn", "joHN"][i],
                    "password": ("doe" if is_valid_attempt else "wrong"),
                },
            )
            self.assertFormError(
                resp,
                "form",
                None,
                "Too many failed login attempts. Try again later."
                if is_locked
                else "The username and/or password you specified are not correct.",
            )

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL,
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.MANDATORY,
        ACCOUNT_LOGIN_ATTEMPTS_LIMIT=1,
    )
    def test_login_failed_attempts_exceeded_cleared_on_password_reset(self):
        # Ensure that login attempts, once they hit the limit,
        # can use the password reset mechanism to regain access.
        user = get_user_model().objects.create(
            username="john", email="john@example.org", is_active=True
        )
        user.set_password("doe")
        user.save()

        EmailAddress.objects.create(
            user=user, email="john@example.org", primary=True, verified=True
        )

        resp = self.client.post(
            reverse("account_login"), {"login": user.email, "password": "bad"}
        )
        self.assertFormError(
            resp,
            "form",
            None,
            "The e-mail address and/or password you specified are not correct.",
        )

        resp = self.client.post(
            reverse("account_login"), {"login": user.email, "password": "bad"}
        )
        self.assertFormError(
            resp,
            "form",
            None,
            "Too many failed login attempts. Try again later.",
        )

        self.client.post(reverse("account_reset_password"), data={"email": user.email})

        body = mail.outbox[0].body
        self.assertGreater(body.find("https://"), 0)

        # Extract URL for `password_reset_from_key` view and access it
        url = body[body.find("/password/reset/") :].split()[0]
        resp = self.client.get(url)
        # Follow the redirect the actual password reset page with the key
        # hidden.
        url = resp.url
        resp = self.client.get(url)
        self.assertTemplateUsed(
            resp,
            "account/password_reset_from_key.%s" % app_settings.TEMPLATE_EXTENSION,
        )
        self.assertFalse("token_fail" in resp.context_data)

        new_password = "newpass123"

        # Reset the password
        resp = self.client.post(
            url, {"password1": new_password, "password2": new_password}
        )
        self.assertRedirects(resp, reverse("account_reset_password_from_key_done"))

        # Check the new password is in effect
        user = get_user_model().objects.get(pk=user.pk)
        self.assertTrue(user.check_password(new_password))

        resp = self.client.post(
            reverse("account_login"),
            {"login": user.email, "password": new_password},
        )

        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL,
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.MANDATORY,
        ACCOUNT_LOGIN_ATTEMPTS_LIMIT=1,
    )
    def test_login_using_unverified_email_address_is_prohibited(self):
        user = get_user_model().objects.create(
            username="john", email="john@example.org", is_active=True
        )
        user.set_password("doe")
        user.save()

        EmailAddress.objects.create(
            user=user, email="john@example.org", primary=True, verified=True
        )
        EmailAddress.objects.create(
            user=user, email="john@example.com", primary=True, verified=False
        )

        resp = self.client.post(
            reverse("account_login"), {"login": "john@example.com", "password": "doe"}
        )
        self.assertRedirects(
            resp,
            reverse("account_email_verification_sent"),
            fetch_redirect_response=False,
        )
        self.assertEqual(len(mail.outbox), 1)
        assert mail.outbox[0].to == ["john@example.com"]

    def test_login_unverified_account_mandatory(self):
        """Tests login behavior when email verification is mandatory."""
        user = get_user_model().objects.create(username="john")
        user.set_password("doe")
        user.save()
        EmailAddress.objects.create(
            user=user, email="user@example.com", primary=True, verified=False
        )
        resp = self.client.post(
            reverse("account_login"), {"login": "john", "password": "doe"}
        )
        self.assertRedirects(resp, reverse("account_email_verification_sent"))

    def test_login_inactive_account(self):
        """
        Tests login behavior with inactive accounts.

        Inactive user accounts should be prevented from performing any actions,
        regardless of their verified state.
        """
        # Inactive and verified user account
        user = get_user_model().objects.create(username="john", is_active=False)
        user.set_password("doe")
        user.save()
        EmailAddress.objects.create(
            user=user, email="john@example.com", primary=True, verified=True
        )
        resp = self.client.post(
            reverse("account_login"), {"login": "john", "password": "doe"}
        )
        self.assertRedirects(resp, reverse("account_inactive"))

        # Inactive and unverified user account
        user = get_user_model().objects.create(username="doe", is_active=False)
        user.set_password("john")
        user.save()
        EmailAddress.objects.create(
            user=user, email="user@example.com", primary=True, verified=False
        )
        resp = self.client.post(
            reverse("account_login"), {"login": "doe", "password": "john"}
        )
        self.assertRedirects(resp, reverse("account_inactive"))

    def test_ajax_password_reset(self):
        get_user_model().objects.create(
            username="john", email="john@example.org", is_active=True
        )
        resp = self.client.post(
            reverse("account_reset_password"),
            data={"email": "john@example.org"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["john@example.org"])
        self.assertEqual(resp["content-type"], "application/json")

    def test_ajax_login_fail(self):
        resp = self.client.post(
            reverse("account_login"),
            {},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 400)
        json.loads(resp.content.decode("utf8"))
        # TODO: Actually test something

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.OPTIONAL
    )
    def test_ajax_login_success(self):
        user = get_user_model().objects.create(username="john", is_active=True)
        user.set_password("doe")
        user.save()
        resp = self.client.post(
            reverse("account_login"),
            {"login": "john", "password": "doe"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode("utf8"))
        self.assertEqual(data["location"], "/accounts/profile/")

    def test_email_view(self):
        self._create_user_and_login()
        self.client.get(reverse("account_email"))
        # TODO: Actually test something

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_logout_view_on_get(self):
        c, resp = self._logout_view("get")
        self.assertTemplateUsed(resp, "account/messages/logged_out.txt")

    @override_settings(ACCOUNT_LOGOUT_ON_GET=False)
    def test_logout_view_on_post(self):
        c, resp = self._logout_view("get")
        self.assertTemplateUsed(
            resp, "account/logout.%s" % app_settings.TEMPLATE_EXTENSION
        )

        receiver_mock = Mock()
        user_logged_out.connect(receiver_mock)

        resp = c.post(reverse("account_logout"))

        self.assertTemplateUsed(resp, "account/messages/logged_out.txt")
        receiver_mock.assert_called_once_with(
            sender=get_user_model(),
            request=resp.wsgi_request,
            user=get_user_model().objects.get(username="john"),
            signal=user_logged_out,
        )

        user_logged_out.disconnect(receiver_mock)

    def _logout_view(self, method):
        c = Client()
        user = get_user_model().objects.create(username="john", is_active=True)
        user.set_password("doe")
        user.save()
        c = Client()
        c.login(username="john", password="doe")
        return c, getattr(c, method)(reverse("account_logout"))

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

    @override_settings(ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False)
    def test_account_authenticated_login_redirects_is_false(self):
        self._create_user_and_login()
        resp = self.client.get(reverse("account_login"))
        self.assertEqual(resp.status_code, 200)

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {
                    "min_length": 9,
                },
            }
        ]
    )
    def test_django_password_validation(self):
        resp = self.client.post(
            reverse("account_signup"),
            {
                "username": "johndoe",
                "email": "john@example.com",
                "password1": "johndoe",
                "password2": "johndoe",
            },
        )
        self.assertFormError(resp, "form", None, [])
        self.assertFormError(
            resp,
            "form",
            "password1",
            ["This password is too short. It must contain at least 9 characters."],
        )

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
        confirmation.send()
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
        confirmation.send()
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(reverse("account_confirm_email", args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertFalse(email.verified)

    @override_settings(
        ACCOUNT_USERNAME_VALIDATORS="allauth.account.tests.test_username_validators"
    )
    def test_username_validator(self):
        get_adapter().clean_username("abc")
        self.assertRaises(ValidationError, lambda: get_adapter().clean_username("def"))

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


class EmailFormTests(TestCase):
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


class BaseSignupFormTests(TestCase):
    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True, ACCOUNT_USERNAME_BLACKLIST=["username"]
    )
    def test_username_in_blacklist(self):
        data = {
            "username": "username",
            "email": "user@example.com",
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertFalse(form.is_valid())

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True, ACCOUNT_USERNAME_BLACKLIST=["username"]
    )
    def test_username_not_in_blacklist(self):
        data = {
            "username": "theusername",
            "email": "user@example.com",
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertTrue(form.is_valid())

    @override_settings(ACCOUNT_USERNAME_REQUIRED=True)
    def test_username_maxlength(self):
        data = {
            "username": "username",
            "email": "user@example.com",
        }
        form = BaseSignupForm(data, email_required=True)
        max_length = get_username_max_length()
        field = form.fields["username"]
        self.assertEqual(field.max_length, max_length)
        widget = field.widget
        self.assertEqual(widget.attrs.get("maxlength"), str(max_length))

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True, ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE=True
    )
    def test_signup_email_verification(self):
        data = {
            "username": "username",
            "email": "user@example.com",
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertFalse(form.is_valid())

        data = {
            "username": "username",
            "email": "user@example.com",
            "email2": "user@example.com",
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertTrue(form.is_valid())

        data["email2"] = "anotheruser@example.com"
        form = BaseSignupForm(data, email_required=True)
        self.assertFalse(form.is_valid())


class CustomSignupFormTests(TestCase):
    @override_settings(
        ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE=True,
        ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE=True,
    )
    def test_custom_form_field_order(self):

        expected_field_order = [
            "email",
            "email2",
            "password1",
            "password2",
            "username",
            "last_name",
            "first_name",
        ]

        class TestSignupForm(forms.Form):
            first_name = forms.CharField(max_length=30)
            last_name = forms.CharField(max_length=30)

            field_order = expected_field_order

        class CustomSignupForm(SignupForm, TestSignupForm):
            # ACCOUNT_SIGNUP_FORM_CLASS is only abided by when the
            # BaseSignupForm definition is loaded the first time on Django
            # startup. @override_settings() has therefore no effect.
            pass

        form = CustomSignupForm()
        self.assertEqual(list(form.fields.keys()), expected_field_order)


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create(
            is_active=True, email="john@example.com", username="john"
        )
        user.set_password(user.username)
        user.save()
        self.user = user

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME
    )  # noqa
    def test_auth_by_username(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.username, password=user.username
            ).pk,
            user.pk,
        )
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.email, password=user.username
            ),
            None,
        )

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL
    )  # noqa
    def test_auth_by_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.email, password=user.username
            ).pk,
            user.pk,
        )
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.username, password=user.username
            ),
            None,
        )

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL
    )  # noqa
    def test_auth_by_username_or_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.email, password=user.username
            ).pk,
            user.pk,
        )
        self.assertEqual(
            backend.authenticate(
                request=None, username=user.username, password=user.username
            ).pk,
            user.pk,
        )


class UUIDUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


class UtilsTests(TestCase):
    def setUp(self):
        self.user_id = uuid.uuid4().hex

    def test_url_str_to_pk_identifies_UUID_as_stringlike(self):
        with patch("allauth.account.utils.get_user_model") as mocked_gum:
            mocked_gum.return_value = UUIDUser
            self.assertEqual(url_str_to_user_pk(self.user_id), uuid.UUID(self.user_id))

    def test_pk_to_url_string_identifies_UUID_as_stringlike(self):
        user = UUIDUser(is_active=True, email="john@example.com", username="john")
        self.assertEqual(user_pk_to_url_str(user), str(user.pk))

    @override_settings(ACCOUNT_PRESERVE_USERNAME_CASING=False)
    def test_username_lower_cased(self):
        user = get_user_model()()
        user_username(user, "CamelCase")
        self.assertEqual(user_username(user), "camelcase")
        # TODO: Actually test something
        filter_users_by_username("CamelCase", "FooBar")

    @override_settings(ACCOUNT_PRESERVE_USERNAME_CASING=True)
    def test_username_case_preserved(self):
        user = get_user_model()()
        user_username(user, "CamelCase")
        self.assertEqual(user_username(user), "CamelCase")
        # TODO: Actually test something
        filter_users_by_username("camelcase", "foobar")

    def test_user_display(self):
        user = get_user_model()(username="john<br/>doe")
        expected_name = "john&lt;br/&gt;doe"
        templates = [
            "{% load account %}{% user_display user %}",
            "{% load account %}{% user_display user as x %}{{ x }}",
        ]
        for template in templates:
            t = Template(template)
            content = t.render(Context({"user": user}))
            self.assertEqual(content, expected_name)


class ConfirmationViewTests(TestCase):
    def _create_user(self, username="john", password="doe"):
        user = get_user_model().objects.create(username=username, is_active=True)
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


class TestResetPasswordForm(TestCase):
    def test_user_email_not_sent_inactive_user(self):
        User = get_user_model()
        User.objects.create_user(
            "mike123", "mike@ixample.org", "test123", is_active=False
        )
        data = {"email": "mike@ixample.org"}
        form = ResetPasswordForm(data)
        self.assertFalse(form.is_valid())


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


class RequestAjaxTests(TestCase):
    def _send_post_request(self, **kwargs):
        return self.client.post(
            reverse("account_signup"),
            {
                "username": "johndoe",
                "email": "john@example.org",
                "email2": "john@example.org",
                "password1": "johndoe",
                "password2": "johndoe",
            },
            **kwargs,
        )

    def test_no_ajax_header(self):
        resp = self._send_post_request()
        self.assertEqual(302, resp.status_code)
        self.assertRedirects(
            resp, settings.LOGIN_REDIRECT_URL, fetch_redirect_response=False
        )

    def test_ajax_header_x_requested_with(self):
        resp = self._send_post_request(HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(settings.LOGIN_REDIRECT_URL, resp.json()["location"])

    def test_ajax_header_http_accept(self):
        resp = self._send_post_request(HTTP_ACCEPT="application/json")
        self.assertEqual(200, resp.status_code)
        self.assertEqual(settings.LOGIN_REDIRECT_URL, resp.json()["location"])
