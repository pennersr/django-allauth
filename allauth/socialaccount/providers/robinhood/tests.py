from allauth.socialaccount.providers import registry
from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse

from .provider import RobinhoodProvider


class RobinhoodTests(create_oauth2_tests(
        registry.by_id(RobinhoodProvider.id))):

    def get_mocked_response(self):
        return MockedResponse(200, """
{
  "username": "test_username",
  "id": "1234-5678-910"
}
        """)
