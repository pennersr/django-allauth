from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.providers.zoho.provider import ZohoProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class ZohoTests(OAuth2TestsMixin, TestCase):
    provider_id = ZohoProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            HTTPStatus.OK,
            """
{"First_Name":"John","Email":"jdoe@example.com",
"Last_Name":"Doe","Display_Name":"JDoee","ZUID":1234567}
""",
        )

    def get_expected_to_str(self):
        return "jdoe@example.com"
