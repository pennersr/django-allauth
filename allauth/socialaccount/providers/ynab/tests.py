# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from importlib import import_module
from requests.exceptions import HTTPError

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase, patch

from .provider import YNABProvider


@override_settings(
    SOCIALACCOUNT_AUTO_SIGNUP=True,
    ACCOUNT_SIGNUP_FORM_CLASS=None, )
# ACCOUNT_EMAIL_VERIFICATION=account_settings
# .EmailVerificationMethod.MANDATORY)
class YNABTests(OAuth2TestsMixin, TestCase):
    provider_id = YNABProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
              {"data": {
        "user":{
        "id": "abcd1234xyz5678"
                    }
                }
              }
        """)

    def test_ynab_compelete_login_401(self):
        from allauth.socialaccount.providers.ynab.views import \
            YNABOAuth2Adapter

        class LessMockedResponse(MockedResponse):
            def raise_for_status(self):
                if self.status_code != 200:
                    raise HTTPError(None)

        request = RequestFactory().get(
            reverse(self.provider.id + '_login'),
            dict(process='login'))

        adapter = YNABOAuth2Adapter(request)
        app = adapter.get_provider().get_app(request)
        token = SocialToken(token='some_token')
        response_with_401 = LessMockedResponse(
            401, """
            {"error": {
              "errors": [{
                "domain": "global",
                "reason": "authError",
                "message": "Invalid Credentials",
                "locationType": "header",
                "location": "Authorization" } ],
              "code": 401,
              "message": "Invalid Credentials" }
            }""")
        with patch(
                'allauth.socialaccount.providers.ynab.views'
                '.requests') as patched_requests:
            patched_requests.get.return_value = response_with_401
            with self.assertRaises(HTTPError):
                adapter.complete_login(request, app, token)


   

