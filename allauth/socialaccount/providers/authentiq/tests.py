# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AuthentiqProvider


class AuthentiqTests(OAuth2TestsMixin, TestCase):
    provider_id = AuthentiqProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, json.dumps({
            "sub": "ZLARGMFT1M",
            "email": "jane@email.invalid",
            "email_verified": True,
            "given_name": "Jane",
            "family_name": "Doe",
        }))
