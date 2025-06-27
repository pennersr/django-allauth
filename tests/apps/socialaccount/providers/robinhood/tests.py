from django.test import TestCase

from allauth.socialaccount.providers.robinhood.provider import RobinhoodProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class RobinhoodTests(OAuth2TestsMixin, TestCase):
    provider_id = RobinhoodProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{
  "username": "test_username",
  "id": "1234-5678-910"
}
        """,
        )

    def get_expected_to_str(self):
        return "test_username"
