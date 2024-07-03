from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import ZohoProvider


class ZohoTests(OAuth2TestsMixin, TestCase):
    provider_id = ZohoProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"First_Name":"John","Email":"jdoe@example.com",
"Last_Name":"Doe","Display_Name":"JDoee","ZUID":1234567}
""",
        )

    def get_expected_to_str(self):
        return "jdoe@example.com"
