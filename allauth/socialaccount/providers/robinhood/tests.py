from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import RobinhoodProvider


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
