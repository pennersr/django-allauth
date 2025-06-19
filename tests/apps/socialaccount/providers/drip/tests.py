from django.test import TestCase

from allauth.socialaccount.providers.drip.provider import DripProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse


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
