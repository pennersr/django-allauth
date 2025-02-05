from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import DigitalOceanProvider


class DigitalOceanTests(OAuth2TestsMixin, TestCase):
    provider_id = DigitalOceanProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
          "account": {
            "droplet_limit": 25,
            "floating_ip_limit": 5,
            "email": "sammy@example.com",
            "uuid": "b6fr89dbf6d9156cace5f3c78dc9851d957381ef",
            "email_verified": true,
            "status": "active",
            "status_message": ""
          }
        }
        """,
        )

    def get_login_response_json(self, with_refresh_token=True):
        return """
        {
          "access_token": "testac",
          "token_type": "bearer",
          "expires_in": 2592000,
          "refresh_token": "00a3aae641658d",
          "scope": "read write",
          "info": {
            "name": "Sammy the Shark",
            "email":"sammy@example.com",
            "uuid":"b6fr89dbf6d9156cace5f3c78dc9851d957381ef"
          }
        }"""

    def get_expected_to_str(self):
        return "sammy@example.com"
