from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import WindowsLiveProvider


class WindowsLiveTests(OAuth2TestsMixin, TestCase):
    provider_id = WindowsLiveProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "first_name": "James",
          "last_name": "Smith",
          "name": "James Smith",
          "locale": "en_US",
          "gender": null,
          "emails": {
              "personal": null,
              "account": "jsmith@example.com",
              "business": null,
              "preferred": "jsmith@example.com"
              },
          "link": "https://profile.live.com/",
          "updated_time": "2014-02-07T00:35:27+0000",
          "id": "83605e110af6ff98"
        }
        """)
