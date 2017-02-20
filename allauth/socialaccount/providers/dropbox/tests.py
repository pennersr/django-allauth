# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DropboxProvider


class DropboxTests(OAuthTestsMixin, TestCase):
    provider_id = DropboxProvider.id

    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Dropbox response
        return [MockedResponse(200, """
    { "uid": "123" }
""")]
