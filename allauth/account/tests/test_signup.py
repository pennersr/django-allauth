from __future__ import absolute_import

import django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.forms import BaseSignupForm, SignupForm
from allauth.account.models import EmailAddress
from allauth.core import context
from allauth.tests import TestCase
from allauth.utils import get_username_max_length


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

    def test_user_class_attribute(self):
        from django.contrib.auth import get_user_model
        from django.db.models.query_utils import DeferredAttribute

        class CustomSignupForm(SignupForm):
            # ACCOUNT_SIGNUP_FORM_CLASS is only abided by when the
            # BaseSignupForm definition is loaded the first time on Django
            # startup. @override_settings() has therefore no effect.
            pass

        User = get_user_model()
        data = {
            "username": "username",
            "email": "user@example.com",
            "password1": "very-secret",
            "password2": "very-secret",
        }
        form = CustomSignupForm(data, email_required=True)

        assert isinstance(User.username, DeferredAttribute)
        form.is_valid()
        assert isinstance(User.username, DeferredAttribute)


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
class SignupTests(TestCase):
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
        Email verification is by-passed, their home email address is
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
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        request.user = AnonymousUser()
        request.session["account_verified_email"] = verified_email
        from allauth.account.views import signup

        with context.request_context(request):
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
        if django.VERSION >= (4, 1):
            self.assertFormError(
                resp.context["form"],
                "password2",
                "You must type the same password each time.",
            )
        else:
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
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        request.user = AnonymousUser()
        from allauth.account.views import signup

        with context.request_context(request):
            signup(request)
        user = get_user_model().objects.get(username="johndoe")
        self.assertEqual(user.email, "john@example.org")

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
        if django.VERSION >= (4, 1):
            self.assertFormError(resp.context["form"], None, [])
            self.assertFormError(
                resp.context["form"],
                "password1",
                ["This password is too short. It must contain at least 9 characters."],
            )
        else:
            self.assertFormError(resp, "form", None, [])
            self.assertFormError(
                resp,
                "form",
                "password1",
                ["This password is too short. It must contain at least 9 characters."],
            )


def test_prevent_enumeration_with_mandatory_verification(settings, user_factory):
    settings.ACCOUNT_PREVENT_ENUMERATION = True
    settings.ACCOUNT_AUTHENTICATION_METHOD = app_settings.AuthenticationMethod.EMAIL
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.MANDATORY
    user = user_factory(username="john", email="john@example.org", password="doe")
    c = Client()
    resp = c.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": user.email,
            "password1": "johndoe",
            "password2": "johndoe",
        },
    )
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_email_verification_sent")
    assertTemplateUsed(resp, "account/email/account_already_exists_message.txt")
    assert EmailAddress.objects.filter(email="john@example.org").count() == 1


def test_prevent_enumeration_off(settings, user_factory):
    settings.ACCOUNT_PREVENT_ENUMERATION = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = app_settings.AuthenticationMethod.EMAIL
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.MANDATORY
    user = user_factory(username="john", email="john@example.org", password="doe")
    c = Client()
    resp = c.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": user.email,
            "password1": "johndoe",
            "password2": "johndoe",
        },
    )
    assert resp.status_code == 200
    assert resp.context["form"].errors == {
        "email": ["A user is already registered with this email address."]
    }


def test_prevent_enumeration_strictly(settings, user_factory):
    settings.ACCOUNT_PREVENT_ENUMERATION = "strict"
    settings.ACCOUNT_AUTHENTICATION_METHOD = app_settings.AuthenticationMethod.EMAIL
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.NONE
    user = user_factory(username="john", email="john@example.org", password="doe")
    c = Client()
    resp = c.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": user.email,
            "password1": "johndoe",
            "password2": "johndoe",
        },
    )
    assert resp.status_code == 302
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert EmailAddress.objects.filter(email="john@example.org").count() == 2


def test_prevent_enumeration_on(settings, user_factory):
    settings.ACCOUNT_PREVENT_ENUMERATION = True
    settings.ACCOUNT_AUTHENTICATION_METHOD = app_settings.AuthenticationMethod.EMAIL
    settings.ACCOUNT_EMAIL_VERIFICATION = app_settings.EmailVerificationMethod.NONE
    user = user_factory(username="john", email="john@example.org", password="doe")
    c = Client()
    resp = c.post(
        reverse("account_signup"),
        {
            "username": "johndoe",
            "email": user.email,
            "password1": "johndoe",
            "password2": "johndoe",
        },
    )
    assert resp.status_code == 200
    assert resp.context["form"].errors == {
        "email": ["A user is already registered with this email address."]
    }


@pytest.mark.django_db
def test_get_initial_with_valid_email():
    """Test that the email field is populated with a valid email."""
    request = RequestFactory().get("/signup/?email=test@example.com")
    from allauth.account.views import signup

    SessionMiddleware(lambda request: None).process_request(request)
    request.user = AnonymousUser()
    with context.request_context(request):
        view = signup(request)
    assert view.context_data["view"].get_initial()["email"] == "test@example.com"
