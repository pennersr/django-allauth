# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import SpotifyOAuth2Provider


class SpotifyOAuth2Tests(create_oauth2_tests(registry.by_id(
        SpotifyOAuth2Provider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """{
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
              "url": "https://fbcdn-profile-a.akamaihd.net/hprofile-ak-frc3/t1.0-1/1970403_10152215092574354_1798272330_n.jpg",
              "width": null
            }
          ],
          "product": "premium",
          "type": "user",
          "uri": "spotify:user:wizzler"
        }""")
