from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import InstagramProvider

class InstagramTests(OAuth2TestsMixin, TestCase):
    provider_id = InstagramProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "meta": {
            "code": 200
          },
          "data": {
            "username": "georgewhewell",
            "bio": "",
            "website": "",
            "profile_picture": "http://images.ak.instagram.com/profiles/profile_11428116_75sq_1339547159.jpg",
            "full_name": "georgewhewell",
            "counts": {
              "media": 74,
              "followed_by": 91,
              "follows": 104
            },
            "id": "11428116"
          }
        }""")
