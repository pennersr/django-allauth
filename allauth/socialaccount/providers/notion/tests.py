from urllib.parse import parse_qs, urlparse

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, mocked_response

from .provider import NotionProvider


class NotionTests(OAuth2TestsMixin, TestCase):
    provider_id = NotionProvider.id
    pkce_enabled_default = False  # Notion does not support PKCE.

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "workspace_id": "workspace-abc",
                "workspace_name": "My Workspace",
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

    def get_expected_to_str(self):
        return "John Doe (My Workspace)"

    def get_login_response_json(self, with_refresh_token=False):
        """
        Docs here:
        https://developers.notion.com/docs/authorization#step-4-notion-responds-with-an-access_token-and-additional-information
        """
        return """
        {
            "access_token": "testac",
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

    def login(self, resp_mock=None, process="login", with_refresh_token=True):
        resp = self.client.post(
            reverse(self.provider.id + "_login")
            + "?"
            + urlencode(dict(process=process))
        )

        p = urlparse(resp["location"])
        q = parse_qs(p.query)

        complete_url = reverse(self.provider.id + "_callback")
        response_json = self.get_login_response_json(
            with_refresh_token=with_refresh_token
        )

        if isinstance(resp_mock, list):
            resp_mocks = resp_mock
        elif resp_mock is None:
            resp_mocks = []
        else:
            resp_mocks = [resp_mock]

        with mocked_response(
            MockedResponse(200, response_json, {"content-type": "application/json"}),
            *resp_mocks,
        ):
            resp = self.client.get(complete_url, self.get_complete_parameters(q))

        return resp
