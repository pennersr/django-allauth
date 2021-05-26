from unittest import expectedFailure

from django.test import override_settings
from django.urls import reverse

from openid.consumer import consumer

from allauth.socialaccount.models import SocialAccount
from allauth.tests import Mock, TestCase, patch
from allauth.utils import get_user_model

from . import views
from .utils import AXAttribute


class OpenIDTests(TestCase):
    def test_discovery_failure(self):
        """
        This used to generate a server 500:
        DiscoveryFailure: No usable OpenID services found
        for http://www.google.com/
        """
        resp = self.client.post(
            reverse("openid_login"), dict(openid="http://www.google.com")
        )
        self.assertTrue("openid" in resp.context["form"].errors)

    @expectedFailure
    def test_login(self):
        # Location: https://s.yimg.com/wm/mbr/html/openid-eol-0.0.1.html
        resp = self.client.post(
            reverse(views.login), dict(openid="http://me.yahoo.com")
        )
        assert "login.yahooapis" in resp["location"]
        with patch(
            "allauth.socialaccount.providers" ".openid.views._openid_consumer"
        ) as consumer_mock:
            client = Mock()
            complete = Mock()
            consumer_mock.return_value = client
            client.complete = complete
            complete_response = Mock()
            complete.return_value = complete_response
            complete_response.status = consumer.SUCCESS
            complete_response.identity_url = "http://dummy/john/"
            with patch(
                "allauth.socialaccount.providers" ".openid.utils.SRegResponse"
            ) as sr_mock:
                with patch(
                    "allauth.socialaccount.providers" ".openid.utils.FetchResponse"
                ) as fr_mock:
                    sreg_mock = Mock()
                    ax_mock = Mock()
                    sr_mock.fromSuccessResponse = sreg_mock
                    fr_mock.fromSuccessResponse = ax_mock
                    sreg_mock.return_value = {}
                    ax_mock.return_value = {AXAttribute.PERSON_FIRST_NAME: ["raymond"]}
                    resp = self.client.post(reverse("openid_callback"))
                    self.assertRedirects(
                        resp,
                        "/accounts/profile/",
                        fetch_redirect_response=False,
                    )
                    get_user_model().objects.get(first_name="raymond")

    @expectedFailure
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
    def test_login_with_extra_attributes(self):
        with patch("allauth.socialaccount.providers.openid.views.QUERY_EMAIL", True):
            resp = self.client.post(
                reverse(views.login), dict(openid="http://me.yahoo.com")
            )
        assert "login.yahooapis" in resp["location"]
        with patch(
            "allauth.socialaccount.providers" ".openid.views._openid_consumer"
        ) as consumer_mock:
            client = Mock()
            complete = Mock()
            endpoint = Mock()
            consumer_mock.return_value = client
            client.complete = complete
            complete_response = Mock()
            complete.return_value = complete_response
            complete_response.endpoint = endpoint
            complete_response.endpoint.server_url = "http://me.yahoo.com"
            complete_response.status = consumer.SUCCESS
            complete_response.identity_url = "http://dummy/john/"
            with patch(
                "allauth.socialaccount.providers" ".openid.utils.SRegResponse"
            ) as sr_mock:
                with patch(
                    "allauth.socialaccount.providers" ".openid.utils.FetchResponse"
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
                    resp = self.client.post(reverse("openid_callback"))
                    self.assertRedirects(
                        resp,
                        "/accounts/profile/",
                        fetch_redirect_response=False,
                    )
                    socialaccount = SocialAccount.objects.get(
                        user__first_name="raymond"
                    )
                    self.assertEqual(socialaccount.extra_data.get("phone"), "123456789")
