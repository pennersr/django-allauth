from django.test import TestCase

from allauth.socialaccount.providers.asana.provider import AsanaProvider
from tests.apps.socialaccount.base import OAuth2TestsMixin
from tests.mocking import MockedResponse


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

    def get_expected_to_str(self):
        return "test@example.com"
