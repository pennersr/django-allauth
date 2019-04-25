from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import SlackProvider


class SlackOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = SlackProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """{
          "ok": true,
          "url": "https:\\/\\/myteam.slack.com\\/",
          "team": {
            "name": "My Team",
            "id": "T12345"
          },
          "user": {
            "name": "cal",
            "email": "cal@example.com",
            "id": "U12345"
          }
        }""")  # noqa
