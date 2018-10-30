# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DropboxOAuth2Provider


class DropboxOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = DropboxOAuth2Provider.id

    def get_mocked_response(self):
        payload = {
            "account_id": "dbid:ASDFasd3ASdfasdFAsd1AS2ASDF1aS-DfAs",
            "account_type": {".tag": "basic"},
            "country": "US",
            "disabled": False,
            "email": "allauth@example.com",
            "email_verified": True,
            "is_paired": True,
            "locale": "en",
            "name": {
                "abbreviated_name": "AA",
                "display_name": "All Auth",
                "familiar_name": "All",
                "given_name": "All",
                "surname": "Auth"
            },
            "profile_photo_url": ("https://dl-web.dropbox.com/account_photo"
                                  "/get/dbid%ASDFasd3ASdfasdFAsd1AS2ASDF1aS"
                                  "-DfAs?size=128x128"),
            "referral_link": "https://db.tt/ASDfAsDf"
        }
        return [MockedResponse(200, json.dumps(payload))]
