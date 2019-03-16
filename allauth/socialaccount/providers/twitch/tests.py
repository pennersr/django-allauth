from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import TwitchProvider


class TwitchTests(OAuth2TestsMixin, TestCase):
    provider_id = TwitchProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "data": [{
            "id": "44322889",
            "login": "dallas",
            "display_name": "dallas",
            "type": "staff",
            "broadcaster_type": "",
            "description": "Just a gamer playing games and chatting. :)",
            "profile_image_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/dallas-profile_image-1a2c906ee2c35f12-300x300.png",
            "offline_image_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/dallas-channel_offline_image-1a2c906ee2c35f12-1920x1080.png",
            "view_count": 191836881,
            "email": "login@provider.com"
          }]
        }
        """)  # noqa
