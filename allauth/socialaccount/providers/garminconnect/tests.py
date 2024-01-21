import json


from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import GarminConnectProvider


class GarminConnectTests(OAuthTestsMixin, TestCase):
    provider_id = GarminConnectProvider.id

    def get_mocked_response(self):
        data = {"userId": 1234567890}
        return [MockedResponse(200, json.dumps(data))]
