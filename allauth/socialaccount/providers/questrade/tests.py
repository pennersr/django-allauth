from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import QuestradeProvider


class QuestradeTests(OAuth2TestsMixin, TestCase):
    provider_id = QuestradeProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{"userId":400,"accounts":[]}""",
        )

    def get_expected_to_str(self):
        return "Questrade"
