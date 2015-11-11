# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import StripeProvider


class StripeTests(create_oauth2_tests(registry.by_id(StripeProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """{
          "id": "acct_sometestid",
          "object": "account",
          "business_logo": null,
          "business_name": null,
          "business_url": "test.com",
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
          "email": "test@test.com",
          "managed": false,
          "metadata": {},
          "statement_descriptor": "TEST.COM",
          "support_phone": "+460123456789",
          "timezone": "Europe/Stockholm",
          "transfers_enabled": true
        }""")

    def get_login_response_json(self, with_refresh_token=True):
        rt = ''
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return """{
            "uid":"weibo",
            "access_token":"testac",
            "livemode": false,
            "token_type": "bearer",
            "stripe_publishable_key": "pk_test_someteskey",
            "stripe_user_id": "acct_sometestid",
            "scope": "read_write"
            %s }""" % rt
