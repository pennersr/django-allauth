from __future__ import absolute_import

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.socialaccount.providers import registry
from allauth.tests import MockedResponse

from .provider import VKProvider


class VKTests(create_oauth2_tests(registry.by_id(VKProvider.id))):

    def get_mocked_response(self, verified_email=True):
        return MockedResponse(200, """
{"response": [{"last_name": "Penners", "university_name": "", "photo": "http://vk.com/images/camera_c.gif", "sex": 2, "photo_medium": "http://vk.com/images/camera_b.gif", "relation": "0", "timezone": 1, "photo_big": "http://vk.com/images/camera_a.gif", "uid": 219004864, "universities": [], "city": "1430", "first_name": "Raymond", "faculty_name": "", "online": 1, "counters": {"videos": 0, "online_friends": 0, "notes": 0, "audios": 0, "photos": 0, "followers": 0, "groups": 0, "user_videos": 0, "albums": 0, "friends": 0}, "home_phone": "", "faculty": 0, "nickname": "", "screen_name": "id219004864", "has_mobile": 1, "country": "139", "university": 0, "graduation": 0, "activity": "", "last_seen": {"time": 1377805189}}]}
""")

    def get_login_response_json(self, with_refresh_token=True):
        return '{"user_id": 219004864, "access_token":"testac"}'
