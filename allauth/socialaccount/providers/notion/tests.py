from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import NotionProvider


class NotionTests(OAuth2TestsMixin, TestCase):

    provider_id = NotionProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """{
            "workspace_id": "workspace-abc",
            "owner":{
              "user": {
                "id": "test123",
                "name": "John Doe",
                "avatar_url": "",
                "person": {
                  "email": "john@acme.com"
                }
              }
            }
        }""",
        )
