from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import FirefoxAccountsProvider


class FirefoxAccountsTests(OAuth2TestsMixin, TestCase):
    provider_id = FirefoxAccountsProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "uid":"6d940dd41e636cc156074109b8092f96",
            "email":"user@example.com"
        }""",
        )
