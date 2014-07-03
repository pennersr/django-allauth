from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import MSLiveProvider

class MSLiveTests(create_oauth2_tests(registry.by_id(MSLiveProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
          "first_name": "James", 
          "last_name": "Smith", 
          "name": "James Smith", 
          "locale": "en_US", 
          "gender": None, 
          "emails": {
              "personal": None, 
              "account": "jsmith@xyz.net", 
              "business": None, 
              "preferred": "jsmith@xyz.net"
              }, 
          "link": "https://profile.live.com/", 
          "updated_time": "2014-02-07T00:35:27+0000",
          "id": "83605e110af6ff98"
        }""")
