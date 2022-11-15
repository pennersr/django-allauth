# -*- coding: utf-8 -*-
import json
from unittest import TestSuite

from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
    provider_classes,
)
from allauth.socialaccount.tests import OpenIDConnectTests
from allauth.tests import Mock, MockedResponse, TestCase, patch

from ... import app_settings


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

    def test_oidc_base_and_provider_settings_sync(self):
        # Retrieve settings via this OpenID Connect server's specific provider ID
        provider_settings = self.provider.get_settings()
        # Retrieve settings via the base OpenID Connect provider ID
        oidc_server_settings = app_settings.PROVIDERS[OpenIDConnectProvider.id][
            "SERVERS"
        ]
        # Find the matching entry in the base OpenID Connect provider's servers list
        matching_servers = list(
            filter(
                lambda server_settings: server_settings["id"]
                == provider_settings["id"],
                oidc_server_settings,
            )
        )
        # Make sure there's only one matching entry and that it's identical
        self.assertEqual(len(matching_servers), 1)
        self.assertDictEqual(matching_servers[0], provider_settings)


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
