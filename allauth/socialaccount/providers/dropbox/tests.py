# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import DropboxProvider


class DropboxTests(create_oauth_tests(registry.by_id(DropboxProvider.id))):
    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Dropbox response
        return [MockedResponse(200, u"""
    { "uid": "123" }
""")]
