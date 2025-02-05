from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import StripeProvider


class StripeTests(OAuth2TestsMixin, TestCase):
    provider_id = StripeProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
          "id": "acct_sometestid",
          "object": "account",
          "business_logo": null,
          "business_name": null,
          "business_url": "example.com",
          "charges_enabled": true,
          "country": "SE",
          "currencies_supported": [
            "usd",
            "eur",
            "sek"
          ],
          "default_currency": "eur",
          "details_submitted": true,
          "display_name": "Test",
          "email": "test@example.com",
          "managed": false,
          "metadata": {},
          "statement_descriptor": "TEST.COM",
          "support_phone": "+460123456789",
          "timezone": "Europe/Stockholm",
          "transfers_enabled": true
        }""",
        )

    def get_expected_to_str(self):
        return "test@example.com"

    def get_login_response_json(self, with_refresh_token=True):
        rt = ""
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return (
            """{
            "uid":"weibo",
            "access_token":"testac",
            "livemode": false,
            "token_type": "bearer",
            "stripe_publishable_key": "pk_test_someteskey",
            "stripe_user_id": "acct_sometestid",
            "scope": "read_write"
            %s }"""
            % rt
        )
