# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import SalesforceProvider


class SalesforceProviderTest(OAuth2TestsMixin, TestCase):
    provider_id = SalesforceProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """{
          "user_id": "acct_sometestid"
        }""")

    def get_login_response_json(self, with_refresh_token=True):
        rt = ''
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return """{
            "id":"weibo",
            "access_token":"testac",
            "token_type": "bearer",
            "scope": "read_write"
            %s }""" % rt
