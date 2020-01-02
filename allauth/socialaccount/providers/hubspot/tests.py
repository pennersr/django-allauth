from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import HubSpotProvider


class HubSpotTests(OAuth2TestsMixin, TestCase):
    provider_id = HubSpotProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "data": [{
            "username": "login@provider.com"
          }]
        }
        """)  # noqa
