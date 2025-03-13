from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import TumblrOAuth2Provider


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
