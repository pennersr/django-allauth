# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import TumblrProvider


class TumblrTests(create_oauth_tests(registry.by_id(TumblrProvider.id))):
    def get_mocked_response(self):
        return [MockedResponse(200, u"""
{
   "meta": {
      "status": 200,
      "msg": "OK"
   },
   "response": {
     "user": {
       "following": 263,
       "default_post_format": "html",
       "name": "derekg",
       "likes": 606,
       "blogs": [
          {
           "name": "derekg",
           "title": "Derek Gottfrid",
           "url": "http://derekg.org/",
           "tweet": "auto",
           "primary": true,
           "followers": 33004929
          },
          {
           "name": "ihatehipstrz",
           "title": "I Hate Hipstrz"
           }
        ]
     }
} }
""")]
