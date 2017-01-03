from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import KakaoProvider


class KakaoTests(OAuth2TestsMixin, TestCase):
    provider_id = KakaoProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
{
"id": 347514800,
"properties": {
"thumbnail_image":
"http://mud-kage.kakao.co.kr/14/dn/btqfiLU5UyB/YVsnjWyjGbr63VEUnxJA40/o.jpg",
"nickname": "\uc774\uc0c1\ud601",
"profile_image":
"http://mud-kage.kakao.co.kr/14/dn/btqficlJTd6/OORvqlHejQvk2l1wNZCC1k/o.jpg"
}
}
""")
