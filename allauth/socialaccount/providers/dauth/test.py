from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import DAuthProvider


class DAuthTests(OAuth2TestsMixin, TestCase):
    provider_id = DAuthProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{"email":"108119069@nitt.edu",
             "id":9,
             "name":"name",
             "phoneNumber":"+7878978976",
             "gender":"MALE",
             "createdAt":"2021-08-17T05:44:58.574Z",
             "updatedAt":"2021-12-08T19:16:52.174Z"
             }""",
        )
