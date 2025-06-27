from django.test import TestCase

from allauth.socialaccount.providers.okta.provider import OktaProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class OktaTests(OAuth2TestsMixin, TestCase):
    provider_id = OktaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "sub": "00u33ow83pjQpCQJr1j8",
                "name": "Jon Smith",
                "locale": "AE",
                "email": "jsmith@example.com",
                "nickname": "Jon Smith",
                "preferred_username": "jsmith@example.com",
                "given_name": "Jon",
                "family_name": "Smith",
                "zoneinfo": "America/Los_Angeles",
                "updated_at": 1601285210,
                "email_verified": true
            }
        """,
        )

    def get_expected_to_str(self):
        return "jsmith@example.com"
