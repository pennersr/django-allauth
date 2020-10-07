# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.keycloak.provider import KeycloakProvider
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class KeycloakTests(OAuth2TestsMixin, TestCase):
    provider_id = KeycloakProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "picture": "https://secure.gravatar.com/avatar/123",
                "email": "mr.bob@your.Keycloak.server.example.com",
                "id": 2,
                "sub": 2,
                "identities": [],
                "name": "Mr Bob"
            }
        """,
        )
