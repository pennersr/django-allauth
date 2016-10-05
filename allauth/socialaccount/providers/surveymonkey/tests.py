# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import SurveyMonkey2Provider


class SurveyMonkeyOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = SurveyMonkey2Provider.id

    def get_mocked_response(self):
        return [MockedResponse(200, """{
          "status": 0,
          "data": {
            "user_details": {
              "username": "USERNAME",
              "account_type": "select_yearly",
              "is_paid_account": false,
              "user_id": 12345678,
              "is_enterprise_user": false
            }
          }
        }""")]
