from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import KakaoProvider


class KakaoTests(OAuth2TestsMixin, TestCase):
    provider_id = KakaoProvider.id

    kakao_data = """
        {
            "id": 233652912,
            "kakao_account": {
                "has_email": true,
                "is_email_valied": true,
                "is_email_verified": true,
                "email": "example@example.com",
                "has_age_range": true,
                "age_range": "20~29",
                "has_birthday": true,
                "birthday": "0101",
                "has_gender": true,
                "gender": female"
            }
            "properties": {
                "thumbnail_image": "http://k.kakaocdn.net/example/ex_1.jpg",
                "profile_image": "http://k.kakaocdn.net/exmaple/ex_2.jpg",
                "nickname": "\uc548\uc8fc\uc740"
            }
        }
    """

    def get_mocked_response(self, data=None):
        if data is None:
            data = self.kakao_data
        return MockedResponse(200, data)

