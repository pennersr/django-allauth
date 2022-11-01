# -*- coding: utf-8 -*-
import json
from unittest import TestSuite

from allauth.socialaccount.providers.openid_connect.provider import (
    provider_classes,
)
from allauth.socialaccount.tests import OpenIDConnectTests
from allauth.tests import Mock, MockedResponse, TestCase, patch


class OpenIDConnectTestsBase(OpenIDConnectTests):
    provider_id = None
    oidc_info_content = {
        "authorization_endpoint": "/login",
        "userinfo_endpoint": "/userinfo",
        "token_endpoint": "/token",
    }
    userinfo_content = {
        "picture": "https://secure.gravatar.com/avatar/123",
        "email": "ness@some.oidc.server.onett.example",
        "id": 1138,
        "sub": 2187,
        "identities": [],
        "name": "Ness",
    }
    extra_data = {
        "picture": "https://secure.gravatar.com/avatar/123",
        "email": "ness@some.oidc.server.onett.example",
        "id": 2187,
        "identities": [],
        "name": "Ness",
    }

    def setUp(self):
        super(OpenIDConnectTestsBase, self).setUp()
        patcher = patch(
            "allauth.socialaccount.providers.openid_connect.views.requests",
            get=Mock(side_effect=self._mocked_responses),
        )
        self.mock_requests = patcher.start()
        self.addCleanup(patcher.stop)

    def get_mocked_response(self):
        # Enable test_login in OAuth2TestsMixin, but this response mock is unused
        return True

    def _mocked_responses(self, url, *args, **kwargs):
        if url.endswith("/.well-known/openid-configuration"):
            return MockedResponse(200, json.dumps(self.oidc_info_content))
        elif url.endswith("/userinfo"):
            return MockedResponse(200, json.dumps(self.userinfo_content))


def _test_class_factory(provider_class):
    class Provider_OpenIDConnectTests(OpenIDConnectTestsBase, TestCase):
        provider_id = provider_class.id

    Provider_OpenIDConnectTests.__name__ = (
        "Provider_OpenIDConnectTests_" + provider_class.id
    )
    return Provider_OpenIDConnectTests


def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for provider_class in provider_classes:
        suite.addTests(
            loader.loadTestsFromTestCase(_test_class_factory(provider_class))
        )
    return suite
