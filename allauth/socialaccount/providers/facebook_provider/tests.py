import json

from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from allauth.account import app_settings as account_settings
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase, mocked_response

from .provider import FacebookProvider


@override_settings(
    SOCIALACCOUNT_AUTO_SIGNUP=True,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    LOGIN_REDIRECT_URL="/accounts/profile/",
    ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.NONE,
    SOCIALACCOUNT_PROVIDERS={"facebook": {"AUTH_PARAMS": {}, "VERIFIED_EMAIL": False}},
)
class FacebookTests(OAuth2TestsMixin, TestCase):
    provider_id = FacebookProvider.id

    facebook_data = """
        {
           "id": "630595557",
           "name": "Raymond Penners",
           "first_name": "Raymond",
           "last_name": "Penners",
           "email": "raymond.penners@example.com",
           "link": "https://www.facebook.com/raymond.penners",
           "username": "raymond.penners",
           "birthday": "07/17/1973",
           "work": [
              {
                 "employer": {
                    "id": "204953799537777",
                    "name": "IntenCT"
                 }
              }
           ],
           "timezone": 1,
           "locale": "nl_NL",
           "verified": true,
           "updated_time": "2012-11-30T20:40:33+0000"
        }"""

    def get_mocked_response(self, data=None):
        if data is None:
            data = self.facebook_data
        return MockedResponse(200, data)

    def test_username_conflict(self):
        User = get_user_model()
        User.objects.create(username="raymond.penners")
        self.login(self.get_mocked_response())
        socialaccount = SocialAccount.objects.get(uid="630595557")
        self.assertEqual(socialaccount.user.username, "raymond")

    def test_username_based_on_provider(self):
        self.login(self.get_mocked_response())
        socialaccount = SocialAccount.objects.get(uid="630595557")
        self.assertEqual(socialaccount.user.username, "raymond.penners")

    def test_username_based_on_provider_with_simple_name(self):
        data = '{"id": "1234567", "name": "Harvey McGillicuddy"}'
        self.login(self.get_mocked_response(data=data))
        socialaccount = SocialAccount.objects.get(uid="1234567")
        self.assertEqual(socialaccount.user.username, "harvey")

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "facebook": {
                "METHOD": "js_sdk",
            }
        },
    )
    def test_media_js(self):
        request = RequestFactory().get(reverse("account_login"))
        request.session = {}
        script = self.provider.media_js(request)
        self.assertTrue('"appId": "app123id"' in script)

    def test_token_auth(self):
        with mocked_response(
            {"access_token": "app_token"},
            {
                "data": {
                    "app_id": "app123id",
                    "is_valid": True,
                }
            },
            self.get_mocked_response(),
        ):
            login = self.provider.verify_token(None, {"access_token": "dummy"})
            assert login.user.email == "raymond.penners@example.com"
            assert login.token.token == "dummy"

    def test_login_by_token(self):
        resp = self.client.get(reverse("account_login"))
        with mocked_response(
            {"access_token": "app_token"},
            {
                "data": {
                    "app_id": "app123id",
                    "is_valid": True,
                }
            },
            self.get_mocked_response(),
        ):
            resp = self.client.post(
                reverse("facebook_login_by_token"),
                data={"access_token": "dummy"},
            )
            self.assertRedirects(
                resp, "/accounts/profile/", fetch_redirect_response=False
            )

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            "facebook": {
                "METHOD": "js_sdk",
                "AUTH_PARAMS": {"auth_type": "reauthenticate"},
                "VERIFIED_EMAIL": False,
            }
        }
    )
    def test_login_by_token_reauthenticate(self):
        resp = self.client.get(reverse("account_login"))
        nonce = json.loads(resp.context["fb_data"])["loginOptions"]["auth_nonce"]
        with mocked_response(
            {"access_token": "app_token"},
            {
                "data": {
                    "app_id": "app123id",
                    "is_valid": True,
                }
            },
            {"auth_nonce": nonce},
            self.get_mocked_response(),
        ):
            resp = self.client.post(
                reverse("facebook_login_by_token"),
                data={"access_token": "dummy"},
            )
            self.assertRedirects(
                resp, "/accounts/profile/", fetch_redirect_response=False
            )

    @override_settings(SOCIALACCOUNT_PROVIDERS={"facebook": {"VERIFIED_EMAIL": True}})
    def test_login_verified(self):
        emailaddress = self._login_verified()
        self.assertTrue(emailaddress.verified)

    def test_login_unverified(self):
        emailaddress = self._login_verified()
        self.assertFalse(emailaddress.verified)

    def _login_verified(self):
        self.login(self.get_mocked_response())
        return EmailAddress.objects.get(email="raymond.penners@example.com")
