# -*- coding: utf-8 -*-
from unittest import TestSuite

from allauth.socialaccount.providers.openid_connect.provider import (
    provider_classes,
)
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase, patch


class OpenIDConnectTestsBase(OAuth2TestsMixin):
    provider_id = None

    @patch("allauth.socialaccount.providers.openid_connect.views.requests")
    def login(self, resp_mock, mock_requests, *args, **kwargs):
        mock_requests.get.return_value = MockedResponse(
            200,
            """
            {
                "authorization_endpoint": "/login",
                "userinfo_endpoint": "/userinfo",
                "token_endpoint": "/token"
            }
            """,
        )
        return super(OpenIDConnectTestsBase, self).login(resp_mock, *args, **kwargs)

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "picture": "https://secure.gravatar.com/avatar/123",
                "email": "ness@some.oidc.server.onett.example",
                "id": 1138,
                "sub": 2187,
                "identities": [],
                "name": "Ness"
            }
        """,
        )


def _test_class_factory(provider_class):
    class Provider_OpenIDConnectTests(OpenIDConnectTestsBase, TestCase):
        provider_id = provider_class.id

    return Provider_OpenIDConnectTests


def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for provider_class in provider_classes:
        suite.addTests(
            loader.loadTestsFromTestCase(_test_class_factory(provider_class))
        )
    return suite
