from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import BaiduProvider

class BaiduTests(create_oauth2_tests(registry.by_id(BaiduProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """{"portrait": "78c0e9839de59bbde7859ccf43", "uname": "\u90dd\u56fd\u715c", "uid": "3225892368"}""")
