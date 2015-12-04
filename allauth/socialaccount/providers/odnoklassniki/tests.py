# -*- coding: utf-8 -*-

from __future__ import absolute_import

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import OdnoklassnikiProvider


class OdnoklassnikiTests(OAuth2TestsMixin, TestCase):
    provider_id = OdnoklassnikiProvider.id

    def get_mocked_response(self, verified_email=True):
        return MockedResponse(200, """
{"uid":"561999209121","birthday":"1999-09-09","age":33,"first_name":"Ivan","last_name":"Petrov","name":"Ivan Petrov","locale":"en","gender":"male","has_email":true,"location":{"city":"Moscow","country":"RUSSIAN_FEDERATION","countryCode":"RU","countryName":"Russia"},"online":"web","pic_1":"http://i500.mycdn.me/res/stub_50x50.gif","pic_2":"http://usd1.mycdn.me/res/stub_128x96.gif"}
""")

    def get_login_response_json(self, with_refresh_token=True):
        return '{"access_token": "testac"}'  # noqa
