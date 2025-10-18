from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.providers.vk.provider import VKProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class VKTests(OAuth2TestsMixin, TestCase):
    provider_id = VKProvider.id

    def get_mocked_response(self, verified_email=True):
        return MockedResponse(
            HTTPStatus.OK,
            """
{
    "user": {
        "user_id": "1234567890",
        "first_name": "Ivan",
        "last_name": "I.",
        "phone": "79991234567",
        "avatar": "http://avatar.com/12345678",
        "email": "ivan_i123@vk.ru",
        "sex": 2,
        "verified": false,
        "birthday": "01.01.2000"
    }
}
""",
        )

    def get_expected_to_str(self):
        return "ivan_i123@vk.ru"

    def get_login_response_json(self, with_refresh_token=True):
        return """
{
  "access_token": "testac",
  "refresh_token": "XXXXX",
  "expires_in": 0,
  "user_id": 1234567890,
  "state": "XXX",
  "scope": "email phone"
}
"""
