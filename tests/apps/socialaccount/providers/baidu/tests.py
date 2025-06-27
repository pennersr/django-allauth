from django.test import TestCase

from allauth.socialaccount.providers.baidu.provider import BaiduProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class BaiduTests(OAuth2TestsMixin, TestCase):
    provider_id = BaiduProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"portrait": "78c0e9839de59bbde7859ccf43",
"uname": "\u90dd\u56fd\u715c", "uid": "3225892368"}""",
        )

    def get_expected_to_str(self):
        return "\u90dd\u56fd\u715c"
