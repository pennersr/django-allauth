from django.test import TestCase

from allauth.socialaccount.providers.reddit.provider import RedditProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


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
