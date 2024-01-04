from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import PingIdentityProvider


class PingIdentityTests(OAuth2TestsMixin, TestCase):
    provider_id = PingIdentityProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
              "sub": "ABCD123456",
              "lastName": "Smith",
              "manager": "ABCD654321",
              "employeeID": "ABCD123456",
              "preferred_username": "ABCD123456",
              "managerName": "Bloggs, Joe",
              "employeeNumber": "12345678",
              "division": "Allauth Management",
              "firstName": "Jon",
              "company": "Allauth Test",
              "state": "null",
              "email": "jsmith@example.com",
              "jobTitle": "Test User"
            }
        """,
        )
