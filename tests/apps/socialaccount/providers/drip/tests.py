from django.test import TestCase

from allauth.socialaccount.providers.drip.provider import DripProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class DripTests(OAuth2TestsMixin, TestCase):
    provider_id = DripProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "users":[{
                "email": "john@acme.com",
                "name": "John Doe",
                "time_zone": "America/Los_Angeles"
            }]
        }""",
        )

    def get_expected_to_str(self):
        return "john@acme.com"
