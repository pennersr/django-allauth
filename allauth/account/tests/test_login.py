from __future__ import absolute_import

import json

import django
from django.conf import settings
from django.core import mail
from django.test.utils import override_settings
from django.urls import reverse

from allauth.account import app_settings
from allauth.account.models import EmailAddress
from allauth.tests import TestCase
from allauth.utils import get_user_model


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
class LoginTests(TestCase):
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
            if django.VERSION >= (4, 1):
                self.assertFormError(
                    resp.context["form"],
                    None,
                    "Too many failed login attempts. Try again later."
                    if is_locked
                    else "The username and/or password you specified are not correct.",
                )
            else:
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
        if django.VERSION >= (4, 1):
            self.assertFormError(
                resp.context["form"],
                None,
                "The email address and/or password you specified are not correct.",
            )
        else:
            self.assertFormError(
                resp,
                "form",
                None,
                "The email address and/or password you specified are not correct.",
            )

        resp = self.client.post(
            reverse("account_login"), {"login": user.email, "password": "bad"}
        )
        if django.VERSION >= (4, 1):
            self.assertFormError(
                resp.context["form"],
                None,
                "Too many failed login attempts. Try again later.",
            )
        else:
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

    @override_settings(ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False)
    def test_account_authenticated_login_redirects_is_false(self):
        self._create_user_and_login()
        resp = self.client.get(reverse("account_login"))
        self.assertEqual(resp.status_code, 200)
