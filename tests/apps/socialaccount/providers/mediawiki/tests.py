from django.test import TestCase

from allauth.socialaccount.providers.mediawiki.provider import MediaWikiProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class MediaWikiTests(OAuth2TestsMixin, TestCase):
    provider_id = MediaWikiProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
                {
                    "iss": "https://meta.wikimedia.org",
                    "sub": 12345,
                    "aud": "1234567890abcdef",
                    "exp": 946681300,
                    "iat": 946681200,
                    "username": "John Doe",
                    "editcount": 123,
                    "confirmed_email": true,
                    "blocked": false,
                    "registered": "20000101000000",
                    "groups": ["*", "user", "autoconfirmed"],
                    "rights": ["read", "edit"],
                    "grants": ["basic"],
                    "email": "johndoe@example.com"
                }
            """,
        )

    def get_expected_to_str(self):
        return "John Doe"
