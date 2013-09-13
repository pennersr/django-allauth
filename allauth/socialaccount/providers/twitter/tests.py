# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import TwitterProvider


class TwitterTests(create_oauth_tests(registry.by_id(TwitterProvider.id))):
    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Twitter response
        return MockedResponse(200, u"""
    { "id": "123" }
""")
