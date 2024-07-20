import json

from django.test.client import RequestFactory
from django.test.utils import override_settings

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AuthentiqProvider
from .views import AuthentiqOAuth2Adapter


class AuthentiqTests(OAuth2TestsMixin, TestCase):
    provider_id = AuthentiqProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            json.dumps(
                {
                    "sub": "ZLARGMFT1M",
                    "email": "jane@email.invalid",
                    "email_verified": True,
                    "given_name": "Jane",
                    "family_name": "Doe",
                }
            ),
        )

    def get_expected_to_str(self):
        return "jane@email.invalid"

    @override_settings(
        SOCIALACCOUNT_QUERY_EMAIL=False,
    )
    def test_default_scopes_no_email(self):
        scopes = self.provider.get_default_scope()
        self.assertIn("aq:name", scopes)
        self.assertNotIn("email", scopes)

    @override_settings(
        SOCIALACCOUNT_QUERY_EMAIL=True,
    )
    def test_default_scopes_email(self):
        scopes = self.provider.get_default_scope()
        self.assertIn("aq:name", scopes)
        self.assertIn("email", scopes)

    def test_scopes(self):
        request = RequestFactory().get(AuthentiqOAuth2Adapter.authorize_url)
        scopes = self.provider.get_scope_from_request(request)
        self.assertIn("openid", scopes)
        self.assertIn("aq:name", scopes)

    def test_dynamic_scopes(self):
        request = RequestFactory().get(
            AuthentiqOAuth2Adapter.authorize_url, dict(scope="foo")
        )
        scopes = self.provider.get_scope_from_request(request)
        self.assertIn("openid", scopes)
        self.assertIn("aq:name", scopes)
        self.assertIn("foo", scopes)

    @override_settings(
        SOCIALACCOUNT_QUERY_EMAIL=True,
        SOCIALACCOUNT_EMAIL_REQUIRED=True,
        SOCIALACCOUNT_EMAIL_VERIFICATION=True,
    )
    def test_scopes_required_verified_email(self):
        request = RequestFactory().get(AuthentiqOAuth2Adapter.authorize_url)
        scopes = self.provider.get_scope_from_request(request)
        self.assertIn("email~rs", scopes)
        self.assertNotIn("email", scopes)

    @override_settings(
        SOCIALACCOUNT_QUERY_EMAIL=True,
        SOCIALACCOUNT_EMAIL_REQUIRED=False,
        SOCIALACCOUNT_EMAIL_VERIFICATION=True,
    )
    def test_scopes_optional_verified_email(self):
        request = RequestFactory().get(AuthentiqOAuth2Adapter.authorize_url)
        scopes = self.provider.get_scope_from_request(request)
        self.assertIn("email~s", scopes)
        self.assertNotIn("email", scopes)

    @override_settings(
        SOCIALACCOUNT_QUERY_EMAIL=True,
        SOCIALACCOUNT_EMAIL_REQUIRED=True,
        SOCIALACCOUNT_EMAIL_VERIFICATION=False,
    )
    def test_scopes_required_email(self):
        request = RequestFactory().get(AuthentiqOAuth2Adapter.authorize_url)
        scopes = self.provider.get_scope_from_request(request)
        self.assertIn("email~r", scopes)
        self.assertNotIn("email", scopes)

    @override_settings(
        SOCIALACCOUNT_QUERY_EMAIL=True,
        SOCIALACCOUNT_EMAIL_REQUIRED=False,
        SOCIALACCOUNT_EMAIL_VERIFICATION=False,
    )
    def test_scopes_optional_email(self):
        request = RequestFactory().get(AuthentiqOAuth2Adapter.authorize_url)
        scopes = self.provider.get_scope_from_request(request)
        self.assertIn("email", scopes)
