from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import RedditProvider


class RedditTests(OAuth2TestsMixin, TestCase):
    provider_id = RedditProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                """{
        "name": "wayward710"}""",
            )
        ]

    def get_expected_to_str(self):
        return "wayward710"
