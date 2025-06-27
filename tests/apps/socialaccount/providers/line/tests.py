from django.test import TestCase

from allauth.socialaccount.providers.line.provider import LineProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class LineTests(OAuth2TestsMixin, TestCase):
    provider_id = LineProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{
"userId": "u7d47d26a6bab09b95695ff02d1a36e38",
"displayName": "\uc774\uc0c1\ud601",
"pictureUrl":
"http://dl.profile.line-cdn.net/0m055ab14d725138288331268c45ac5286a35482fb794a"
}""",
        )

    def get_expected_to_str(self):
        return "\uc774\uc0c1\ud601"
