from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import MailcowProvider


class MailcowTests(OAuth2TestsMixin, TestCase):
    provider_id = MailcowProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "success": true,
            "username": "user@example.com",
            "id": "user@example.com",
            "identifier": "user@example.com",
            "email": "user@example.com",
            "full_name": "Test User",
            "displayName": "Test User",
            "created": "2021-12-15 14:35:54",
            "modified": "2023-11-02 09:37:58",
            "active": 1
        }
        """,
        )

    def get_expected_to_str(self):
        return "user@example.com"
