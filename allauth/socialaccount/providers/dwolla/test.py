from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DwollaProvider


class DwollaTests(OAuth2TestsMixin, TestCase):
    provider_id = DwollaProvider.id

    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Dropbox response
        return [MockedResponse(200, """{
            "id": "123",
        }""")]
