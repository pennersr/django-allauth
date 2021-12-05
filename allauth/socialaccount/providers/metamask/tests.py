from __future__ import unicode_literals
from django.test.utils import override_settings

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import TestCase, MockedResponse, patch
from django.urls import reverse

from .provider import MetamaskProvider

SOCIALACCOUNT_PROVIDERS = {"metamask": {"ChainID": "6969"}}


class MetamaskTests(TestCase):
    @override_settings(SOCIALACCOUNT_PROVIDERS=SOCIALACCOUNT_PROVIDERS)
    def test_login(self):
        with patch(
            "allauth.socialaccount.providers.persona.views.requests"
        ) as requests_mock:
            requests_mock.post.return_value.json.return_value = {
                "status": "okay",
                "account": "0xfbfa21e9931f647bd6cc5be9e1a0dd9a41da535e",
            }

            resp = self.client.post(reverse("metamask_login"), dict(assertion="dummy"))
            self.assertRedirects(
                resp, "/accounts/profile/", fetch_redirect_response=False
            )
            get_user_model().objects.get(username="0xfbfa21e9931f647bd6cc5be9e1a0dd9a41da535e")
