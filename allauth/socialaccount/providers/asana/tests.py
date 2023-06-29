from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AsanaProvider


class AsanaTests(OAuth2TestsMixin, TestCase):
    provider_id = AsanaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"data": {"photo": null, "workspaces": [{"id": 31337, "name": "example.com"},
{"id": 3133777, "name": "Personal Projects"}], "email": "test@example.com",
"name": "Test Name", "id": 43748387}}""",
        )
