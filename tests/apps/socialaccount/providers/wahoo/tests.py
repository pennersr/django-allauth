from django.test import TestCase

from allauth.socialaccount.providers.wahoo.provider import WahooProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse


class WahooTests(OAuth2TestsMixin, TestCase):
    provider_id = WahooProvider.id

    def get_mocked_response(self):
        # https://cloud-api.wahooligan.com/#users
        return MockedResponse(
            200,
            """
            {
              "id": 60462,
              "height": "2.0",
              "weight": "80.0",
              "first": "Bob",
              "last": "Smith",
              "email": "sample@test-domain.com",
              "birth": "1980-10-02",
              "gender": 1,
              "created_at": "2018-10-23T15:38:23.000Z",
              "updated_at": "2018-10-24T20:46:40.000Z"
            }
        """,
        )

    def get_expected_to_str(self):
        return "sample@test-domain.com"
