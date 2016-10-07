from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase
from .provider import BattleNetProvider
from .views import _check_errors


class BattleNetTests(OAuth2TestsMixin, TestCase):
    provider_id = BattleNetProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "battletag": "LuckyDragon#1953",
            "id": "123456789"
        }""")

    def test_invalid_data(self):
        with self.assertRaises(OAuth2Error):
            # No id, raises
            _check_errors({})

        with self.assertRaises(OAuth2Error):
            _check_errors({"error": "invalid_token"})

        _check_errors({"id": 12345})  # Does not raise
