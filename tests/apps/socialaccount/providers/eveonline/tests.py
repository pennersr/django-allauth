from django.test import TestCase

from allauth.socialaccount.providers.eveonline.provider import EveOnlineProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class EveOnlineTests(OAuth2TestsMixin, TestCase):
    provider_id = EveOnlineProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "CharacterID": 273042051,
            "CharacterName": "CCP illurkall",
            "ExpiresOn": "2014-05-23T15:01:15.182864Z",
            "Scopes": " ",
            "TokenType": "Character",
            "CharacterOwnerHash": "XM4D...FoY="
        }""",
        )

    def get_expected_to_str(self):
        return "CCP illurkall"
