from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import EveOnlineProvider


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
