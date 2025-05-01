import urllib.error
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

import pytest
from openid import fetchers
from openid.consumer import consumer

from allauth.socialaccount.models import SocialAccount

from . import views
from .utils import AXAttribute


class TestFetcher(fetchers.Urllib2Fetcher):
    def fetch(self, url, body=None, headers=None):
        if url == "https://steamcommunity.com/openid":
            return fetchers.HTTPResponse(
                final_url="https://steamcommunity.com/openid",
                status=200,
                headers={"content-type": "application/xrds+xml;charset=utf-8"},
                body='<?xml version="1.0" encoding="UTF-8"?>\n<xrds:XRDS xmlns:xrds="xri://$xrds" xmlns="xri://$xrd*($v*2.0)">\n\t<XRD>\n\t\t<Service priority="0">\n\t\t\t<Type>http://specs.openid.net/auth/2.0/server</Type>\t\t\n\t\t\t<URI>https://steamcommunity.com/openid/login</URI>\n\t\t</Service>\n\t</XRD>\n</xrds:XRDS>',
            )
        if url == "https://steamcommunity.com/openid/login":
            return fetchers.HTTPResponse(
                final_url="https://steamcommunity.com/openid/login",
                status=200,
                headers={"content-type": "text/plain;charset=utf-8"},
                body="ns:http://specs.openid.net/auth/2.0\nerror_code:unsupported-type\nerror:Associations not supported\n",
            )

        if url == "https://discovery-failure.com/":
            raise urllib.error.URLError
        ret = super().fetch(url, body=body, headers=headers)
        breakpoint()
        return ret


@pytest.fixture(autouse=True)
def setup_fetcher():
    old_fetcher = fetchers.getDefaultFetcher()
    fetchers.setDefaultFetcher(TestFetcher())
    yield
    fetchers.setDefaultFetcher(old_fetcher)


def test_discovery_failure(client):
    """
    This used to generate a server 500:
    DiscoveryFailure: No usable OpenID services found
    for http://www.google.com/
    """
    resp = client.post(
        reverse("openid_login"), dict(openid="https://discovery-failure.com/")
    )
    assert "openid" in resp.context["form"].errors


def test_login(client, db):
    # Location: https://s.yimg.com/wm/mbr/html/openid-eol-0.0.1.html
    resp = client.post(
        reverse(views.login), dict(openid="https://steamcommunity.com/openid")
    )
    assert "steamcommunity.com/openid/login" in resp["location"]
    with patch(
        "allauth.socialaccount.providers.openid.views._openid_consumer"
    ) as consumer_mock:
        consumer_client = Mock()
        complete = Mock()
        consumer_mock.return_value = consumer_client
        consumer_client.complete = complete
        complete_response = Mock()
        complete.return_value = complete_response
        complete_response.status = consumer.SUCCESS
        complete_response.identity_url = "http://dummy/john/"
        with patch(
            "allauth.socialaccount.providers.openid.utils.SRegResponse"
        ) as sr_mock:
            with patch(
                "allauth.socialaccount.providers.openid.utils.FetchResponse"
            ) as fr_mock:
                sreg_mock = Mock()
                ax_mock = Mock()
                sr_mock.fromSuccessResponse = sreg_mock
                fr_mock.fromSuccessResponse = ax_mock
                sreg_mock.return_value = {}
                ax_mock.return_value = {AXAttribute.PERSON_FIRST_NAME: ["raymond"]}
                resp = client.post(reverse("openid_callback"))
                assert resp["location"] == "/accounts/profile/"
                get_user_model().objects.get(first_name="raymond")
                social_account = SocialAccount.objects.get(
                    uid=complete_response.identity_url
                )
                account = social_account.get_provider_account()
                assert account.to_str() == complete_response.identity_url


@override_settings(
    SOCIALACCOUNT_PROVIDERS={
        "openid": {
            "SERVERS": [
                dict(
                    id="yahoo",
                    name="Yahoo",
                    openid_url="http://me.yahoo.com",
                    extra_attributes=[
                        (
                            "phone",
                            "http://axschema.org/contact/phone/default",
                            True,
                        )
                    ],
                )
            ]
        }
    }
)
def test_login_with_extra_attributes(client, db):
    with patch("allauth.socialaccount.providers.openid.views.QUERY_EMAIL", True):
        resp = client.post(
            reverse(views.login), dict(openid="https://steamcommunity.com/openid")
        )
    assert "steamcommunity.com/openid/login" in resp["location"]
    with patch(
        "allauth.socialaccount.providers.openid.views._openid_consumer"
    ) as consumer_mock:
        consumer_client = Mock()
        complete = Mock()
        endpoint = Mock()
        consumer_mock.return_value = consumer_client
        consumer_client.complete = complete
        complete_response = Mock()
        complete.return_value = complete_response
        complete_response.endpoint = endpoint
        complete_response.endpoint.server_url = "http://me.yahoo.com"
        complete_response.status = consumer.SUCCESS
        complete_response.identity_url = "http://dummy/john/"
        with patch(
            "allauth.socialaccount.providers.openid.utils.SRegResponse"
        ) as sr_mock:
            with patch(
                "allauth.socialaccount.providers.openid.utils.FetchResponse"
            ) as fr_mock:
                sreg_mock = Mock()
                ax_mock = Mock()
                sr_mock.fromSuccessResponse = sreg_mock
                fr_mock.fromSuccessResponse = ax_mock
                sreg_mock.return_value = {}
                ax_mock.return_value = {
                    AXAttribute.CONTACT_EMAIL: ["raymond@example.com"],
                    AXAttribute.PERSON_FIRST_NAME: ["raymond"],
                    "http://axschema.org/contact/phone/default": ["123456789"],
                }
                resp = client.post(reverse("openid_callback"))
                assert resp["location"] == "/accounts/profile/"
                socialaccount = SocialAccount.objects.get(user__first_name="raymond")
                assert socialaccount.extra_data.get("phone") == "123456789"
