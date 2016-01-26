from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import BaiduProvider

class BaiduTests(OAuth2TestsMixin, TestCase):
    provider_id = BaiduProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """{"portrait": "78c0e9839de59bbde7859ccf43", "uname": "\u90dd\u56fd\u715c", "uid": "3225892368"}""")
