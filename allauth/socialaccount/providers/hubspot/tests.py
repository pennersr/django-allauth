from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import HubSpotProvider


class HubSpotTests(OAuth2TestsMixin, TestCase):
    provider_id = HubSpotProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
    "email": "user@example.com",
}
""")

    def get_login_response_json(self, with_refresh_token=True):
        return '{\
    "refresh_token": "testrc",\
    "access_token": "testac",\
    "expires_in": "3600",\
}'
