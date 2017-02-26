# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OnedriveOAuth2Provider


class OnedriveOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = OnedriveOAuth2Provider.id

    def get_mocked_response(self):
        return [MockedResponse(200, """{
          "id" : "contact.c1678ab4000000000000000000000000",
          "first_name" : "Roberto",
          "last_name" : "Tamburello",
          "name" : "Roberto Tamburello",
          "gender" : "male",
          "locale" : "en_US"
        } """)]
