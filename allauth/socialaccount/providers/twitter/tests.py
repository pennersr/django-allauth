# -*- coding: utf-8 -*-
from allauth.socialaccount.tests import create_oauth_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import TwitterProvider


class TwitterTests(create_oauth_tests(registry.by_id(TwitterProvider.id))):
    def get_mocked_response(self):
        # FIXME: Replace with actual/complete Twitter response
        return [MockedResponse(200, r"""
{"follow_request_sent": false,
 "profile_use_background_image": true,
 "id": 45671919, "verified": false, "profile_text_color": "333333",
 "profile_image_url_https":
       "https://pbs.twimg.com/profile_images/793142149/r_normal.png",
 "profile_sidebar_fill_color": "DDEEF6",
 "is_translator": false, "geo_enabled": false, "entities":
 {"description": {"urls": []}}, "followers_count": 43, "protected": false,
 "location": "The Netherlands", "default_profile_image": false,
 "id_str": "45671919", "status": {"contributors": null, "truncated":
  false, "text": "RT @denibertovic: Okay I'm definitely using django-allauth from now on. So easy to set up, far less time consuming, and it just works. #dja\u2026", "in_reply_to_status_id": null, "id": 400658301702381568, "favorite_count": 0, "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>", "retweeted": true, "coordinates": null, "entities": {"symbols": [], "user_mentions": [{"indices": [3, 16], "screen_name": "denibertovic", "id": 23508244, "name": "Deni Bertovic", "id_str": "23508244"}], "hashtags": [{"indices": [135, 139], "text": "dja"}], "urls": []}, "in_reply_to_screen_name": null, "id_str": "400658301702381568", "retweet_count": 6, "in_reply_to_user_id": null, "favorited": false, "retweeted_status": {"lang": "en", "favorited": false, "in_reply_to_user_id": null, "contributors": null, "truncated": false, "text": "Okay I'm definitely using django-allauth from now on. So easy to set up, far less time consuming, and it just works. #django", "created_at": "Sun Jul 28 19:56:26 +0000 2013", "retweeted": true, "in_reply_to_status_id": null, "coordinates": null, "id": 361575897674956800, "entities": {"symbols": [], "user_mentions": [], "hashtags": [{"indices": [117, 124], "text": "django"}], "urls": []}, "in_reply_to_status_id_str": null, "in_reply_to_screen_name": null, "source": "web", "place": null, "retweet_count": 6, "geo": null, "in_reply_to_user_id_str": null, "favorite_count": 8, "id_str": "361575897674956800"}, "geo": null, "in_reply_to_user_id_str": null, "lang": "en", "created_at": "Wed Nov 13 16:15:57 +0000 2013", "in_reply_to_status_id_str": null, "place": null}, "utc_offset": 3600, "statuses_count": 39, "description": "", "friends_count": 83, "profile_link_color": "0084B4", "profile_image_url": "http://pbs.twimg.com/profile_images/793142149/r_normal.png", "notifications": false, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png", "profile_background_color": "C0DEED", "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png", "name": "Raymond Penners", "lang": "nl", "profile_background_tile": false, "favourites_count": 0, "screen_name": "pennersr", "url": null, "created_at": "Mon Jun 08 21:10:45 +0000 2009", "contributors_enabled": false, "time_zone": "Amsterdam", "profile_sidebar_border_color": "C0DEED", "default_profile": true, "following": false, "listed_count": 1} """)]  # noqa

    def test_login(self):
        account = super(TwitterTests, self).test_login()
        tw_account = account.get_provider_account()
        self.assertEqual(tw_account.get_screen_name(),
                         'pennersr')
        self.assertEqual(tw_account.get_avatar_url(),
                         'http://pbs.twimg.com/profile_images/793142149/r.png')
        self.assertEqual(tw_account.get_profile_url(),
                         'http://twitter.com/pennersr')
