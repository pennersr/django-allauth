from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase
from .provider import BattleNetProvider


class BattleNetTests(OAuth2TestsMixin, TestCase):
    provider_id = BattleNetProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "battletag": "LuckyDragon#1953",
            "id": "123456789"
        }""")
