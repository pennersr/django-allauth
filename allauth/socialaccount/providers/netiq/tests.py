from allauth.socialaccount.providers.netiq.provider import NetIQProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class NetIQTests(OAuth2TestsMixin, TestCase):
    provider_id = NetIQProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "sub": "d4c094dd899ab0408fb9d4c094dd899a",
                "acr": "secure/name/password/uri",
                "preferred_username": "Mocktest",
                "email": "mocktest@your.netiq.server.example.com",
                "nickname": "Mocktest",
                "family_name": "test",
                "given_name": "Mock",
                "website": "https://www.exanple.com"
            }
        """,
        )

    def get_expected_to_str(self):
        return "mocktest@your.netiq.server.example.com"
