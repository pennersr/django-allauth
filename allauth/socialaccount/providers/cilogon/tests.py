from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import CILogonProvider


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
