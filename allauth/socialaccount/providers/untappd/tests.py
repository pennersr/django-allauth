from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import UntappdProvider


class UntappdTests(OAuth2TestsMixin, TestCase):
    provider_id = UntappdProvider.id

    def get_login_response_json(self, with_refresh_token=True):
        return """
            {
                "meta": {
                    "http_code": 200
                },
                "response": {
                    "access_token": "testac"
                }
            }"""

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{
   "meta":{
      "code":200,
      "response_time":{
         "time":0.29,
         "measure":"seconds"
      },
      "init_time":{
         "time":0.011,
         "measure":"seconds"
      }
   },
   "notifications":{
      "type":"notifications",
      "unread_count":{
         "comments":0,
         "toasts":0,
         "friends":0,
         "messages":0,
         "news":0
      }
   },
   "response":{
      "user":{
         "uid":123456,
         "id":123456,
         "user_name":"groovecoder",
         "first_name":"",
         "last_name":"",
         "user_avatar":"https:\\/\\/gravatar.com\\/avatar\\/ec25d046746de3be33779256f6957d8f?size=100&d=https%3A%2F%2Funtappd.akamaized.net%2Fsite%2Fassets%2Fimages%2Fdefault_avatar_v2.jpg%3Fv%3D1",
         "user_avatar_hd":"https:\\/\\/gravatar.com\\/avatar\\/ec25d046746de3be33779256f6957d8f?size=125&d=https%3A%2F%2Funtappd.akamaized.net%2Fsite%2Fassets%2Fimages%2Fdefault_avatar_v2.jpg%3Fv%3D1",
         "user_cover_photo":"https:\\/\\/untappd.akamaized.net\\/site\\/assets\\/v3\\/images\\/cover_default.jpg",
         "user_cover_photo_offset":0,
         "is_private":0,
         "location":"Testville",
         "url":"",
         "bio":"",
         "is_supporter":0,
         "relationship":"self",
         "untappd_url":"http:\\/\\/untappd.com\\/user\\/testuser",
         "account_type":"user",
         "stats":{
            "total_badges":43,
            "total_friends":43,
            "total_checkins":73,
            "total_beers":61,
            "total_created_beers":1,
            "total_followings":9,
            "total_photos":31
         },
         "recent_brews":{},
         "checkins":{},
         "media":{},
         "contact":{},
         "date_joined":"Tue, 11 Dec 2012 14:27:53 +0000",
         "settings":{
            "badge":{
               "badges_to_facebook":1,
               "badges_to_twitter":1
            },
            "checkin":{
               "checkin_to_facebook":0,
               "checkin_to_twitter":0,
               "checkin_to_foursquare":0
            },
            "navigation":{
               "default_to_checkin":0
            },
            "email_address":"test@example.com"
         }
      }
   }
}
        """,
        )

    def get_expected_to_str(self):
        return "groovecoder"
