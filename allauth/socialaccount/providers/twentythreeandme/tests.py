from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import TwentyThreeAndMeProvider


class TwentyThreeAndMeTests(OAuth2TestsMixin, TestCase):
    provider_id = TwentyThreeAndMeProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "profiles": [
                {"id": "56c46bdb0902f8e2", "genotyped": false}
            ],
            "id": "b4b975a5a6a1b80b"
        }
        """,
        )

    def get_expected_to_str(self):
        return "23andMe"

    def get_login_response_json(self, with_refresh_token=True):
        return """
        {
            "access_token":"testac",
            "token_type":"bearer",
            "expires_in": 86400,
            "refresh_token":"33c53cd7bb",
            "scope":"basic"
        }"""
