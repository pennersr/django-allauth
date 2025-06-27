from django.test import TestCase

from allauth.socialaccount.providers.dwolla.provider import DwollaProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class DwollaTests(OAuth2TestsMixin, TestCase):
    provider_id = DwollaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "id": "123",
            "_links":{"account":{"href":"http://localhost"}},
            "name":"John Doe"
        }""",
        )

    def get_login_response_json(self, with_refresh_token=True):
        rt = ""
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return (
            """{
            "uid":"weibo",
            "access_token":"testac",
            "_links":{"account":{"href":"http://localhost"}}
            %s }"""
            % rt
        )

    def get_expected_to_str(self):
        return "John Doe"
