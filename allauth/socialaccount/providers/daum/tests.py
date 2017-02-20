import json

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DaumProvider


class DaumTests(OAuth2TestsMixin, TestCase):
    provider_id = DaumProvider.id

    def get_mocked_response(self):
        result = dict()
        result['userid'] = '38DTh'
        result['id'] = 46287445
        result['nickname'] = 'xncbf'
        result['bigImagePath'] = 'https://img1.daumcdn.net/thumb/'
        result['openProfile'] = 'https://img1.daumcdn.net/thumb/'
        body = dict()
        body['code'] = 200
        body['message'] = 'OK'
        body['result'] = result
        return MockedResponse(200, json.dumps(body))
