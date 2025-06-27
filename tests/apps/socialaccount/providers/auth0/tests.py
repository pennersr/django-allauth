from django.test import TestCase

from allauth.socialaccount.providers.auth0.provider import Auth0Provider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class Auth0Tests(OAuth2TestsMixin, TestCase):
    provider_id = Auth0Provider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "picture": "https://secure.gravatar.com/avatar/123",
                "email": "mr.bob@your.Auth0.server.example.com",
                "id": 2,
                "sub": 2,
                "identities": [],
                "name": "Mr Bob"
            }
        """,
        )

    def get_expected_to_str(self):
        return "mr.bob@your.Auth0.server.example.com"
