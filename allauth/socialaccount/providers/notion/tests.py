import base64
import hashlib
import requests
from urllib.parse import parse_qs, urlparse

from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount import app_settings
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase, mocked_response

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

    def login(self, resp_mock=None, process="login", with_refresh_token=True):
        resp = self.client.post(
            reverse(self.provider.id + "_login")
            + "?"
            + urlencode(dict(process=process))
        )

        p = urlparse(resp["location"])
        q = parse_qs(p.query)

        # Always false.
        pkce_enabled = False

        self.assertEqual("code_challenge" in q, pkce_enabled)
        self.assertEqual("code_challenge_method" in q, pkce_enabled)
        if pkce_enabled:
            code_challenge = q["code_challenge"][0]
            self.assertEqual(q["code_challenge_method"][0], "S256")

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

            # Find the access token POST request, and assert that it contains
            # the correct code_verifier if and only if PKCE is enabled
            request_calls = requests.request.call_args_list
            for args, kwargs in request_calls:
                data = kwargs.get("data", {})
                if args[0] == "POST" and isinstance(data, dict):
                    self.assertEqual("code_verifier" in data, pkce_enabled)

                    if pkce_enabled:
                        hashed_code_verifier = hashlib.sha256(
                            data["code_verifier"].encode("ascii")
                        )
                        expected_code_challenge = (
                            base64.urlsafe_b64encode(hashed_code_verifier.digest())
                            .rstrip(b"=")
                            .decode()
                        )
                        self.assertEqual(code_challenge, expected_code_challenge)

        return resp
