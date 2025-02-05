from django.test import TestCase

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse

from .provider import FeishuProvider


class FeishuTests(OAuth2TestsMixin, TestCase):
    provider_id = FeishuProvider.id

    def get_mocked_response(self):
        return [
            MockedResponse(
                0,
                """
                {"data": {"access_token": "testac"}}
                """,
            ),
            MockedResponse(
                0,
                """
                {
                    "code": 0,
                    "data": {
                        "access_token": "u-6U1SbDiM6XIH2DcTCPyeub",
                        "avatar_url": "www.feishu.cn/avatar/icon",
                        "avatar_thumb": "www.feishu.cn/avatar/icon_thumb",
                        "avatar_middle": "www.feishu.cn/avatar/icon_middle",
                        "avatar_big": "www.feishu.cn/avatar/icon_big",
                        "expires_in": 7140,
                        "name": "zhangsan",
                        "en_name": "Three Zhang",
                        "open_id": "ou-caecc734c2e3328a62489fe0648c4b98779515d3",
                        "tenant_key": "736588c92lxf175d",
                        "refresh_expires_in": 2591940,
                        "refresh_token": "ur-t9HHgRCjMqGqIU9v05Zhos",
                        "token_type": "Bearer"
                    }
                }
                """,
            ),
        ]

    def get_expected_to_str(self):
        return "zhangsan"

    def get_login_response_json(self, with_refresh_token=True):
        return """{"app_access_token":"testac"}"""
