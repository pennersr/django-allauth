from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import DingTalkProvider


class DingTalkTests(OAuth2TestsMixin, TestCase):
    provider_id = DingTalkProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "nick": "aiden",
            "unionId": "hTaCSb1nM4RXii6jaQvHZqQiEiE",
            "avatarUrl": "https://static-legacy.dingtalk.com/media/lADPDg7mViaksW3NBJPNBJI_1170_1171.jpg",
            "openId": "ELdCPlk0V2LodZHx3n0p5AiEiE"
            }""",
        )

    def get_login_response_json(self, with_refresh_token=True):
        return """{
    "accessToken": "testac",
    "expireIn": "3600",
    "refreshToken": "testrf"
}"""

    def get_expected_to_str(self):
        return "aiden"
