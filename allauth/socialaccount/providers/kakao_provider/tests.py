from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import KakaoProvider


class KakaoTests(OAuth2TestsMixin, TestCase):
    provider_id = KakaoProvider.id

    kakao_data = """
        {
            "id": 123456789,
            "connected_at": "2022-04-11T01:45:28Z",
            "kakao_account": {
                "profile_nickname_needs_agreement": false,
                "profile_image_needs_agreement": false,
                "profile": {
                    "nickname": "홍길동",
                    "thumbnail_image_url": "http://yyy.kakao.com/.../img_110x110.jpg",
                    "profile_image_url": "http://yyy.kakao.com/dn/.../img_640x640.jpg",
                    "is_default_image":false,
                    "is_default_nickname": false
                },
                "name_needs_agreement":false,
                "name":"홍길동",
                "email_needs_agreement":false,
                "is_email_valid": true,
                "is_email_verified": true,
                "email": "sample@sample.com",
                "age_range_needs_agreement":false,
                "age_range":"20~29",
                "birthyear_needs_agreement": false,
                "birthyear": "2002",
                "birthday_needs_agreement":false,
                "birthday":"1130",
                "birthday_type":"SOLAR",
                "gender_needs_agreement":false,
                "gender":"female",
                "phone_number_needs_agreement": false,
                "phone_number": "+82 010-1234-5678",
                "ci_needs_agreement": false,
                "ci": "CI",
                "ci_authenticated_at": "2019-03-11T11:25:22Z"
            },
            "properties":{
                "CUSTOM_PROPERTY_KEY": "CUSTOM_PROPERTY_VALUE"
            },
            "for_partner": {
                "uuid": "UUID"
            }
        }
    """

    def get_mocked_response(self, data=None):
        if data is None:
            data = self.kakao_data
        return MockedResponse(200, data)
