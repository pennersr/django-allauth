from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import TwitterOAuth2Provider


class TwitterOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = TwitterOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
                "data": {
                    "created_at": "2020-09-02T13:39:14.000Z",
                    "id": "1301152652357595137",
                    "verified": false,
                    "username": "realllkk520",
                    "name": "realllkk520",
                    "profile_image_url": "https://pbs.twimg.com/profile_images/1537259565632593920/OoRGPbUg_normal.jpg"
                }
            }
            """,
        )  # noqa

    def get_expected_to_str(self):
        return "realllkk520"
