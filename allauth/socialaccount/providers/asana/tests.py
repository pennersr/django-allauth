from allauth.socialaccount.providers import registry
from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse

from .provider import AsanaProvider


class AsanaTests(create_oauth2_tests(
        registry.by_id(AsanaProvider.id))):

    def get_mocked_response(self):
        return MockedResponse(200, """
{"data": {"photo": null, "workspaces": [{"id": 31337, "name": "example.com"},
{"id": 3133777, "name": "Personal Projects"}], "email": "test@example.com",
"name": "Test Name", "id": 43748387}}""")
