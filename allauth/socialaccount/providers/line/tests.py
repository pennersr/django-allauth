from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import LineProvider


class LineTests(OAuth2TestsMixin, TestCase):
    provider_id = LineProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "mid":"u7d47d26a6bab09b95695ff02d1a36e38"
        }""")
