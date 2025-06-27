from django.test import TestCase

from allauth.socialaccount.providers.questrade.provider import QuestradeProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class QuestradeTests(OAuth2TestsMixin, TestCase):
    provider_id = QuestradeProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{"userId":400,"accounts":[]}""",
        )

    def get_expected_to_str(self):
        return "Questrade"
