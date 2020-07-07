from django.test.client import RequestFactory
from django.urls import reverse

from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase, mocked_response

from .provider import TwitchProvider
from .views import TwitchOAuth2Adapter


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

    def test_response_over_400_raises_OAuth2Error(self):
        resp_mock = MockedResponse(
            400, '{"error": "Invalid token"}'
        )
        expected_error = "Twitch API Error: Invalid token ()"

        self.check_for_error(resp_mock, expected_error)

    def test_empty_or_missing_data_key_raises_OAuth2Error(self):
        resp_mock = MockedResponse(
            200, '{"data": []}'
        )
        expected_error = "Invalid data from Twitch API: {'data': []}"

        self.check_for_error(
            resp_mock, expected_error)

        resp_mock = MockedResponse(
            200, '{"missing_data": "key"}'
        )
        expected_error = (
            "Invalid data from Twitch API: "
            "{'missing_data': 'key'}"
        )

        self.check_for_error(resp_mock, expected_error)

    def test_missing_twitch_id_raises_OAuth2Error(self):
        resp_mock = MockedResponse(
            200, '{"data": [{"login": "fake_twitch"}]}'
        )
        expected_error = (
            "Invalid data from Twitch API: "
            "{'login': 'fake_twitch'}"
        )

        self.check_for_error(resp_mock, expected_error)

    def check_for_error(self, resp_mock, expected_error):
        with self.assertRaises(OAuth2Error) as error_ctx:
            self._run_just_complete_login(resp_mock)

        self.assertEqual(
            str(error_ctx.exception).replace('u', ''),
            expected_error
        )

    def _run_just_complete_login(self, resp_mock):
        """
        Helper function for checking that Error cases are
        handled correctly. Running only `complete_login` means
        we can check that the specific erros are raised before
        they are caught and rendered to generic error HTML
        """
        request = RequestFactory().get(
            reverse(self.provider.id + '_login'),
            {'process': 'login'},
        )
        adapter = TwitchOAuth2Adapter(request)
        app = adapter.get_provider().get_app(request)
        token = SocialToken(token='this-is-my-fake-token')

        with mocked_response(resp_mock):
            adapter = TwitchOAuth2Adapter(request)
            adapter.complete_login(request, app, token)
