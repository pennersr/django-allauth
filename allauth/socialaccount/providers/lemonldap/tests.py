# -*- coding: utf-8 -*-
from allauth.socialaccount.providers.lemonldap.provider import (
    LemonLDAPProvider,
)
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase


class LemonLDAPTests(OAuth2TestsMixin, TestCase):
    provider_id = LemonLDAPProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "email": "dwho@example.com",
                "sub": "dwho",
                "preferred_username": "dwho",
                "name": "Doctor Who"
            }
        """,
        )
