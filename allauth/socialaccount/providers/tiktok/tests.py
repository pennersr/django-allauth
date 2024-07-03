from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import TikTokProvider


class TikTokTests(OAuth2TestsMixin, TestCase):
    provider_id = TikTokProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
          "data": {
            "user": {
                "open_id": "44322889",
                "username": "username123",
                "display_name": "Nice Display Name",
                "avatar_url": "https://example.com/avatar.jpg",
                "profile_deep_link": "https://example.com/profile"
            }
          }
        }
        """,
        )

    def get_expected_to_str(self):
        return "username123"
