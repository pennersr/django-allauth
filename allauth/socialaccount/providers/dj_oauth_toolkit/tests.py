from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DjOAuthToolkitProvider


class DjOAuthToolkitTests(OAuth2TestsMixin, TestCase):
    provider_id = DjOAuthToolkitProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "sub": "1234567890",
                "email": "joedoe@example.org",
                "username": "joedoe",
                "given_name": "Joe",
                "family_name": "Doe"
            }
            """,
        )
