# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import FiveHundredPxProvider


class FiveHundredPxTests(OAuthTestsMixin, TestCase):
    provider_id = FiveHundredPxProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                200,
                """{
          "user":  {
            "id": 5751454,
            "username": "testuser",
            "firstname": "Test",
            "lastname": "User",
            "birthday": null,
            "sex": 0,
            "city": "San Francisco",
            "state": "California",
            "country": "United States",
            "registration_date": "2015-12-12T03:20:31-05:00",
            "about": "About me.",
            "usertype": 0,
            "fotomoto_on": true,
            "locale": "en",
            "show_nude": false,
            "allow_sale_requests": 1,
            "fullname": "Test User",
            "userpic_url": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/1.jpg?1",
            "userpic_https_url": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/1.jpg?1",
            "cover_url": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/cover_2048.jpg?7",
            "upgrade_status": 2,
            "store_on": true,
            "photos_count": 68,
            "galleries_count": 2,
            "affection": 1888,
            "in_favorites_count": 340,
             "friends_count": 181,
            "followers_count": 150,
            "analytics_code": null,
             "invite_pending": false,
            "invite_accepted": false,
            "email": "test@example.com",
            "shadow_email": "test@example.com",
            "upload_limit": null,
            "upload_limit_expiry": "2016-12-01T13:33:55-05:00",
            "upgrade_type": 2,
            "upgrade_status_expiry": "2017-05-27",
            "auth":  {
              "facebook": 0,
              "twitter": 0,
              "google_oauth2": 0
            },
            "presubmit_for_licensing": null,
            "avatars":  {
              "default":  {
                "http": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/1.jpg?1",
                "https": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/1.jpg?1"
              },
              "large":  {
                "http": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/2.jpg?1",
                "https": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/2.jpg?1"
              },
              "small":  {
                "http": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/1.jpg?1",
                "https": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/1.jpg?1"
              },
              "tiny":  {
                "http": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/4.jpg?1",
                "https": "https://pacdn.500px.org/10599609/8e20991262c468a866918dcbe2f7e9a30e2c2c9c/4.jpg?1"
              }
            }
          }
        }""",
            )
        ]  # noqa
