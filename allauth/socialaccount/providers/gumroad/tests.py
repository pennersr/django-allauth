from django.test import TestCase

from allauth.socialaccount.providers.gumroad.provider import GumroadProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse


class GumroadTests(OAuth2TestsMixin, TestCase):
    provider_id = GumroadProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                "success": true,
                "user": {
                    "bio": "a sailor, a tailor",
                    "name": "John Smith",
                    "twitter_handle": null,
                    "user_id": "G_-mnBf9b1j9A7a4ub4nFQ==",
                    "email": "johnsmith@gumroad.com",
                    "url": "https://gumroad.com/sailorjohn"
                }
            }""",
        )

    def get_expected_to_str(self):
        return "johnsmith@gumroad.com"
