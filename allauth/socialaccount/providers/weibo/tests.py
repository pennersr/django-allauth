from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import WeiboProvider


class WeiboTests(OAuth2TestsMixin, TestCase):
    provider_id = WeiboProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"bi_followers_count": 0,
 "domain": "", "avatar_large": "http://tp3.sinaimg.cn/3195025850/180/0/0",
 "block_word": 0, "star": 0, "id": 3195025850, "city": "1", "verified": false,
 "follow_me": false, "verified_reason": "", "followers_count": 6,
 "location": "\u5317\u4eac \u4e1c\u57ce\u533a", "mbtype": 0,
 "profile_url": "u/3195025850", "province": "11", "statuses_count": 0,
 "description": "", "friends_count": 0, "online_status": 0, "mbrank": 0,
 "idstr": "3195025850",
 "profile_image_url": "http://tp3.sinaimg.cn/3195025850/50/0/0",
 "allow_all_act_msg": false, "allow_all_comment": true, "geo_enabled": true,
 "name": "pennersr", "lang": "zh-cn", "weihao": "", "remark": "",
 "favourites_count": 0, "screen_name": "pennersr", "url": "", "gender": "f",
 "created_at": "Tue Feb 19 19:43:39 +0800 2013", "verified_type": -1,
 "following": false}

""",
        )

    def get_expected_to_str(self):
        return "pennersr"
