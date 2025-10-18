import json
from http import HTTPStatus

from django.test import TestCase

from allauth.socialaccount.providers.daum.provider import DaumProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


class DaumTests(OAuth2TestsMixin, TestCase):
    provider_id = DaumProvider.id

    def get_mocked_response(self):
        result = {}
        result["userid"] = "38DTh"
        result["id"] = 46287445
        result["nickname"] = "xncbf"
        result["bigImagePath"] = "https://img1.daumcdn.net/thumb/"
        result["openProfile"] = "https://img1.daumcdn.net/thumb/"
        body = {}
        body["code"] = HTTPStatus.OK
        body["message"] = "OK"
        body["result"] = result
        return MockedResponse(HTTPStatus.OK, json.dumps(body))

    def get_expected_to_str(self):
        return "xncbf"
