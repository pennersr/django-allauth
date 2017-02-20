import json

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import BattleNetProvider
from .views import _check_errors


class BattleNetTests(OAuth2TestsMixin, TestCase):
    provider_id = BattleNetProvider.id
    _uid = 123456789
    _battletag = "LuckyDragon#1953"

    def get_mocked_response(self):
        data = {"battletag": self._battletag, "id": self._uid}
        return MockedResponse(200, json.dumps(data))

    def test_invalid_data(self):
        with self.assertRaises(OAuth2Error):
            # No id, raises
            _check_errors({})

        with self.assertRaises(OAuth2Error):
            _check_errors({"error": "invalid_token"})

        _check_errors({"id": 12345})  # Does not raise

    def test_extra_data(self):
        self.login(self.get_mocked_response())
        account = SocialAccount.objects.get(uid=str(self._uid))
        self.assertEqual(account.extra_data["battletag"], self._battletag)
        self.assertEqual(account.extra_data["id"], self._uid)
        self.assertEqual(account.extra_data["region"], "us")
