import json

from django.test import TestCase

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import BattleNetProvider
from .views import _check_errors


class BattleNetTests(OAuth2TestsMixin, TestCase):
    provider_id = BattleNetProvider.id
    _uid = 123456789
    _battletag = "LuckyDragon#1953"

    def get_mocked_response(self):
        data = {"battletag": self._battletag, "id": self._uid}
        return MockedResponse(200, json.dumps(data))

    def get_expected_to_str(self):
        return self._battletag

    def test_valid_response_no_battletag(self):
        data = {"id": 12345}
        response = MockedResponse(200, json.dumps(data))
        self.assertEqual(_check_errors(response), data)

    def test_invalid_data(self):
        response = MockedResponse(200, json.dumps({}))
        with self.assertRaises(OAuth2Error):
            # No id, raises
            _check_errors(response)

    def test_profile_invalid_response(self):
        data = {"code": 403, "type": "Forbidden", "detail": "Account Inactive"}
        response = MockedResponse(401, json.dumps(data))

        with self.assertRaises(OAuth2Error):
            # no id, 4xx code, raises
            _check_errors(response)

    def test_error_response(self):
        body = json.dumps({"error": "invalid_token"})
        response = MockedResponse(400, body)

        with self.assertRaises(OAuth2Error):
            # no id, 4xx code, raises
            _check_errors(response)

    def test_service_not_found(self):
        response = MockedResponse(596, "<h1>596 Service Not Found</h1>")
        with self.assertRaises(OAuth2Error):
            # bad json, 5xx code, raises
            _check_errors(response)

    def test_invalid_response(self):
        response = MockedResponse(200, "invalid json data")
        with self.assertRaises(OAuth2Error):
            # bad json, raises
            _check_errors(response)

    def test_extra_data(self):
        self.login(self.get_mocked_response())
        account = SocialAccount.objects.get(uid=str(self._uid))
        self.assertEqual(account.extra_data["battletag"], self._battletag)
        self.assertEqual(account.extra_data["id"], self._uid)
        self.assertEqual(account.extra_data["region"], "us")
