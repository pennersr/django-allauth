from django.contrib.auth import get_user_model
from django.core import validators
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.urls import reverse

from allauth.account import app_settings
from allauth.account.signals import user_logged_out
from allauth.tests import Mock


test_username_validators = [
    validators.RegexValidator(regex=r"^[a-c]+$", message="not abc")
]


@override_settings(
    ACCOUNT_DEFAULT_HTTP_PROTOCOL="https",
    ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.MANDATORY,
    ACCOUNT_LOGIN_METHODS={app_settings.LoginMethod.USERNAME},
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    ACCOUNT_EMAIL_SUBJECT_PREFIX=None,
    LOGIN_REDIRECT_URL="/accounts/profile/",
    ACCOUNT_SIGNUP_REDIRECT_URL="/accounts/welcome/",
    ACCOUNT_ADAPTER="allauth.account.adapter.DefaultAccountAdapter",
    ACCOUNT_USERNAME_REQUIRED=True,
)
class LogoutTests(TestCase):
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
