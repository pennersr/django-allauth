from django.test import TestCase

from allauth.socialaccount.providers.amazon.provider import AmazonProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class AmazonTests(OAuth2TestsMixin, TestCase):
    provider_id = AmazonProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
          "Profile":{
                        "CustomerId":"amzn1.account.K2LI23KL2LK2",
                        "Name":"John Doe",
                        "PrimaryEmail":"johndoe@example.com"
                    }
        }""",
        )

    def get_expected_to_str(self):
        return "johndoe@example.com"
