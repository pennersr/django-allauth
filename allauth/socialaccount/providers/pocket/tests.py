from urllib.parse import parse_qs, urlencode, urlparse

from django.urls import reverse

from allauth.socialaccount.tests import OAuthTestsMixin
from allauth.tests import MockedResponse, TestCase, mocked_response

from .provider import PocketProvider


class PocketOAuthTests(OAuthTestsMixin, TestCase):
    provider_id = PocketProvider.id

    def get_mocked_response(self):
        return []

    def get_expected_to_str(self):
        return "name@example.com"

    def get_access_token_response(self):
        return MockedResponse(
            200,
            """
        {"access_token":"5678defg-5678-defg-5678-defg56",
        "username":"name@example.com"}
        """,
        )

    def login(self, resp_mocks, process="login"):
        with mocked_response(
            MockedResponse(
                200,
                """
                {"code": "dcba4321-dcba-4321-dcba-4321dc"}
                """,
                {"content-type": "application/json"},
            )
        ):
            resp = self.client.post(
                reverse(self.provider.id + "_login")
                + "?"
                + urlencode(dict(process=process))
            )
        p = urlparse(resp["location"])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id + "_callback")
        self.assertGreater(q["redirect_uri"][0].find(complete_url), 0)
        with mocked_response(self.get_access_token_response(), *resp_mocks):
            resp = self.client.get(complete_url)
        return resp
