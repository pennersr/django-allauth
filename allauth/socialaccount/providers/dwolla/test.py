from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DwollaProvider


class DwollaTests(OAuthTestsMixin, TestCase):
    provider_id = DwollaProvider.id

    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Dropbox response
        return [MockedResponse(200, """{ "uid": "123" }""")]
