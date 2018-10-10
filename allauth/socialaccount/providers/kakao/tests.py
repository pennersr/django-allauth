from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import KakaoProvider


class KakaoTests(OAuth2TestsMixin, TestCase):
    provider_id = KakaoProvider.id

    kakao_data = """
        {
            "id": 123456789,
            "properties": {
                "nickname": "\uc9c0\uc724",
                "thumbnail_image": "http://xxx.kakao.co.kr/.../aaa.jpg",
                "profile_image": "http://xxx.kakao.co.kr/.../bbb.jpg"
            },
            "kakao_account": {
                "has_email": true,
                "is_email_valid": true,
                "is_email_verified": true,
                "email": "xxxxxxx@xxxxx.com",
                "has_age_range": true,
                "age_range": "20~29",
                "has_birthday": true,
                "birthday": "1130",
                "has_gender": true,
                "gender": "female"
            }
        }
    """

    def get_mocked_response(self, data=None):
        if data is None:
            data = self.kakao_data
        return MockedResponse(200, data)
