# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import RedditProvider


class RedditTests(create_oauth2_tests(registry.by_id(
        RedditProvider.id))):
    def get_mocked_response(self):
        return [MockedResponse(200, """{
        "name": "wayward710"}""")]
