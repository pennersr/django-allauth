from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import TumblrProvider


class TumblrTests(OAuthTestsMixin, TestCase):
    provider_id = TumblrProvider.id

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
