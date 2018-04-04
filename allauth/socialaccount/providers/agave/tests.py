from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AgaveProvider


class AgaveTests(OAuth2TestsMixin, TestCase):
    provider_id = AgaveProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
        "status": "success",
        "message": "User details retrieved successfully.",
        "version": "2.0.0-SNAPSHOT-rc3fad",
        "result": {
          "first_name": "John",
          "last_name": "Doe",
          "full_name": "John Doe",
          "email": "jon@doe.edu",
          "phone": "",
          "mobile_phone": "",
          "status": "Active",
          "create_time": "20180322043812Z",
          "username": "jdoe"
          }
        }
        """)
