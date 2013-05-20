from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import TwitchProvider

class TwitchTests(create_oauth2_tests(registry.by_id(TwitchProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """{"name":"test_user1","created_at":"2011-06-03T17:49:19Z","updated_at":"2012-06-18T17:19:57Z","_links":{"self":"https://api.twitch.tv/kraken/users/test_user1"},"logo":"http://static-cdn.jtvnw.net/jtv_user_pictures/test_user1-profile_image-62e8318af864d6d7-300x300.jpeg","_id":22761313,"display_name":"test_user1","email":"asdf@asdf.com","partnered":true}

""")

