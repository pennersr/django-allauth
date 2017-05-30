from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import KakaoProvider


class KakaoTests(OAuth2TestsMixin, TestCase):
    provider_id = KakaoProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{"id": 233652912,
"kaccount_email": "insanejflow@example.com",
"kaccount_email_verified": true,
"properties":
{
"thumbnail_image":
"http://mud-kage.kakao.co.kr/14/dn/btqegghHRjx/DbvFZTjNnQpsI8S6hh1cxK/o.jpg",
"profile_image":
"http://mud-kage.kakao.co.kr/14/dn/btqedGORigT/1TwogEZOBWnNkXolo5yVs1/o.jpg",
"nickname": "\uc548\uc8fc\uc740"
}
}
""")
