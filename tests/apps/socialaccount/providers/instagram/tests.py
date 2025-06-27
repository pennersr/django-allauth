from django.test import TestCase

from allauth.socialaccount.providers.instagram.provider import InstagramProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class InstagramTests(OAuth2TestsMixin, TestCase):
    provider_id = InstagramProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
            "username": "georgewhewell",
            "bio": "",
            "website": "",
            "profile_picture":
            "http://images.ak.instagram.com/profiles/profile_11428116_75sq_1339547159.jpg",
            "full_name": "georgewhewell",
            "counts": {
              "media": 74,
              "followed_by": 91,
              "follows": 104
            },
            "id": "11428116"
        }""",
        )  # noqa

    def get_expected_to_str(self):
        return "georgewhewell"
