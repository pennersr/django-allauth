from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import WeixinProvider


class WeixinTests(OAuth2TestsMixin, TestCase):
    provider_id = WeixinProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"access_token":
 "OezXcEiiBSKSxW0eoylIeO5cPxb4Ks1RpbXGMv9uiV35032zNHGzXcld-EKsSScE3gRZMrUU78skCbp1ShtZnR0dQB8Wr_LUf7FA-H97Lnd2HgQah_GnkQex-vPFsGEwPPcNAV6q1Vz3uRNgL0MUFg",
 "city": "Pudong New District",
 "country": "CN",
 "expires_in": 7200,
 "headimgurl":
 "http://wx.qlogo.cn/mmopen/VkvLVEpoJiaibYsVyW8GzxHibzlnqSM7iaX09r6TWUJXCNQHibHz37krvN65HR1ibEpgH5K5sukcIzA3r1C4KQ9qyyX9XIUdY9lNOk/0",
 "language": "zh_CN",
 "nickname": "某某某",
 "openid": "ohS-VwAJ9GEXlplngwybJ3Z-ZHrI",
 "privilege": [],
 "province": "Shanghai",
 "refresh_token":
 "OezXcEiiBSKSxW0eoylIeO5cPxb4Ks1RpbXGMv9uiV35032zNHGzXcld-EKsSScEbMnnMqVExcSpj7KRAuBA8BU2j2e_FK5dgBe-ro32k7OuHtznwqqBn5QR7LZGo2-P8G7gG0eitjyZ751sFlnTAw",
 "scope": "snsapi_login",
 "sex": 1,
 "unionid": "ohHrhwKnD9TOunEW0eKTS45vS5Qo"}""",
        )  # noqa

    def get_expected_to_str(self):
        # For some reason, WeixinOAuth2Adapter.complete_login runs this line:
        # extra_data["nickname"] = nickname.encode("raw_unicode_escape").decode(
        #     "utf-8"
        # )
        return "\\u67d0\\u67d0\\u67d0"
