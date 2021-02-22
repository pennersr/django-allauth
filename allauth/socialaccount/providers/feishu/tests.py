# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from allauth.socialaccount.providers import registry
from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse

from .provider import FeishuProvider


class WeixinTests(create_oauth2_tests(registry.by_id(FeishuProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(
            0,
            """{
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
            """,
        )
