from django.test import TestCase

from allauth.socialaccount.providers.tumblr_oauth2.provider import TumblrOAuth2Provider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class TumblrTests(OAuth2TestsMixin, TestCase):
    provider_id = TumblrOAuth2Provider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                """
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
""",
            )
        ]

    def get_expected_to_str(self):
        return "derekg"
