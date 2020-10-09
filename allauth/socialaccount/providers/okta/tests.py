from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OktaProvider


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
