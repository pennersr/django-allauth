from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import SpotifyOAuth2Provider


class SpotifyOAuth2Tests(OAuth2TestsMixin, TestCase):
    provider_id = SpotifyOAuth2Provider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
          "birthdate": "1937-06-01",
          "country": "SE",
          "display_name": "JM Wizzler",
          "email": "email@example.com",
          "external_urls": {
            "spotify": "https://open.spotify.com/user/wizzler"
          },
          "followers" : {
            "href" : null,
            "total" : 3829
          },
          "href": "https://api.spotify.com/v1/users/wizzler",
          "id": "wizzler",
          "images": [
            {
              "height": null,
              "url":
              "https://fbcdn-profile-a.akamaihd.net/hprofile-ak-frc3/t1.0-1/1970403_10152215092574354_1798272330_n.jpg",
              "width": null
            }
          ],
          "product": "premium",
          "type": "user",
          "uri": "spotify:user:wizzler"
        }""",
        )  # noqa

    def get_expected_to_str(self):
        return "email@example.com"
