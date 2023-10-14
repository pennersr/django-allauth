# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.ebay.provider import EBayProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class EBayTests(OAuth2TestsMixin, TestCase):
    provider_id = EBayProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "access_token": "test_token",
                "expires_in": 3600,
                "token_type": "Bearer",
                "refresh_token": "test_refresh_token",
                "userid": "test_user"
            }
        """,
        )
