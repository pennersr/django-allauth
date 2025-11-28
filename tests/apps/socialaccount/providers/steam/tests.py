from unittest.mock import Mock, patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from openid.yadis.discover import DiscoveryFailure
from pytest_django.asserts import assertRedirects

from allauth.socialaccount.providers.steam import views
from allauth.socialaccount.providers.steam.provider import SteamOpenIDProvider
from tests.apps.socialaccount.base import setup_app


class SteamTests(TestCase):
    def setUp(self):
        self.app = setup_app(SteamOpenIDProvider.id)

    def test_redirect(self):
        with patch(
            "allauth.socialaccount.providers.steam.provider._openid_consumer"
        ) as consumer_mock:
            consumer_client = Mock()
            begin = Mock()
            auth_request = Mock()
            redirectURL = Mock()
            consumer_mock.return_value = consumer_client
            consumer_client.begin = begin
            begin.return_value = auth_request
            auth_request.redirectURL = redirectURL
            redirectURL.return_value = "https://steamcommunity.com/openid/login?XXX"

            resp = self.client.post(reverse(views.steam_login))
            assertRedirects(
                resp,
                "https://steamcommunity.com/openid/login?XXX",
                fetch_redirect_response=False,
            )

    def test_redirect_error(self):
        with patch(
            "allauth.socialaccount.providers.steam.provider._openid_consumer"
        ) as consumer_mock:
            consumer_client = Mock()
            begin = Mock()
            consumer_mock.return_value = consumer_client
            consumer_client.begin = begin

            def discovery_failure(*args, **kwargs):
                raise DiscoveryFailure(
                    "HTTP Response status from identity URL host is not 200. Got status 502",
                    None,
                )

            begin.side_effect = discovery_failure

            resp = self.client.post(reverse(views.steam_login))
            template_ext = getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html")
            self.assertTemplateUsed(
                resp, f"socialaccount/authentication_error.{template_ext}"
            )
