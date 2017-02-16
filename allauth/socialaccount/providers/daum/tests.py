from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DaumProvider


class DaumTests(OAuth2TestsMixin, TestCase):
    provider_id = DaumProvider.id

    def get_mocked_response(self):

        return MockedResponse(200, """
{
"code": 200,
"message": "OK",
"result": {
"userid": "38DTh",
"id": 46287445,
"nickname": "xncbf",
"imagePath": "https://img1.daumcdn.net/thumb/R55x55/?fname=http%3A%2F%2Ftwg.tset.daumcdn.net%2Fprofile%2F-zYQhBX2b-E0&t=1487231948435",
"bigImagePath": "https://img1.daumcdn.net/thumb/R158x158/?fname=http%3A%2F%2Ftwg.tset.daumcdn.net%2Fprofile%2F-zYQhBX2b-E0&t=1487231948435",
"openProfile": true
}
}
""")
