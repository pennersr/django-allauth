# -*- coding: utf-8 -*-
from unittest import TestSuite

from allauth.socialaccount.providers.openid_connect.provider import (
    OpenIDConnectProvider,
    provider_classes,
)
from allauth.socialaccount.tests import OpenIDConnectTests
from allauth.tests import TestCase

from ... import app_settings


class OpenIDConnectTestsBase(OpenIDConnectTests):
    provider_id = None

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
    assert len(
        provider_classes
    ), "No OpenID Connect servers are configured in test_settings.py"
    for provider_class in provider_classes:
        suite.addTests(
            loader.loadTestsFromTestCase(_test_class_factory(provider_class))
        )
    return suite
