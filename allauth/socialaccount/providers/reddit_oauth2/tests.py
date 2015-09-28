# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import RedditOAuth2Provider


class RedditOAuth2Tests(create_oauth2_tests(registry.by_id(
        RedditOAuth2Provider.id))):
    def get_mocked_response(self):
        return [MockedResponse(200, """{
        u'name': u'wayward710', 
        u'created': 1294876805.0, 
        u'hide_from_robots': False, u'gold_creddits': 0, 
        u'created_utc': 1294876805.0, u'link_karma': 1, u'comment_karma': 0, 
        u'over_18': False, 
        u'is_gold': False, 
        u'is_mod': False, 
        u'gold_expiration': None, 
        u'has_verified_email': False, 
        u'id': 
        u'4pxw0', 
        u'inbox_count': 0}""")]
