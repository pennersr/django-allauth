from django.test import TestCase

from allauth.socialaccount.providers.cilogon.provider import CILogonProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class CILogonTests(OAuth2TestsMixin, TestCase):
    provider_id = CILogonProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "email": "johndoe@example.edu",
            "eppn": "u1234567@example.edu",
            "firstname": "John",
            "lastname": "Doe",
            "idp_name": "Example University",
            "sub": "http://cilogon.org/serverA/users/1234567"
        }""",
        )

    def get_expected_to_str(self):
        return "johndoe@example.edu"
