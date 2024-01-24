import json

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import GarminConnectProvider


class GarminConnectTests(OAuthTestsMixin, TestCase):
    provider_id = GarminConnectProvider.id

    def get_mocked_response(self):
        # Garmin only provides userId in the response
        data = {"userId": "d3315b1072421d0dd7c8f6b8e1de4df8"}
        return [MockedResponse(200, json.dumps(data))]
