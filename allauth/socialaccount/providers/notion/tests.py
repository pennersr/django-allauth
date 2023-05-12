from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import NotionProvider


class NotionTests(OAuth2TestsMixin, TestCase):
    provider_id = NotionProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "workspace_id": "workspace-abc",
                "owner": {
                    "user": {
                        "id": "test123",
                        "name": "John Doe",
                        "avatar_url": "",
                        "person": {"email": "john@example.com"},
                    }
                },
            }
            """,
        )  # noqa

    def get_login_response_json(self, with_refresh_token=False):
        """
        Docs here:
        https://developers.notion.com/docs/authorization#step-4-notion-responds-with-an-access_token-and-additional-information
        """
        return """
        {
            "access_token": "test123",
            "bot_id": "bot-abc",
            "duplicated_template_id": "template-abc",
            "owner": {
            "workspace_id": "workspace-abc",
                "user": {
                    "id": "test123",
                    "name": "John Doe",
                    "avatar_url": "",
                    "person": {
                        "email": "john@example.com"
                    }
                }
            },
            "workspace_icon": "https://example.com/icon.png",
            "workspace_id": "workspace-abc",
            "workspace_name": "My Workspace"
        }
        """
