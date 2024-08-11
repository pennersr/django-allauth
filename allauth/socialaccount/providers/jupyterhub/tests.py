from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import JupyterHubProvider


class JupyterHubTests(OAuth2TestsMixin, TestCase):
    provider_id = JupyterHubProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
        {
        "kind": "user",
        "name": "abc",
        "admin": false,
        "groups": [],
        "server": null,
        "pending": null,
        "created": "2016-12-06T18:30:50.297567Z",
        "last_activity": "2017-02-07T17:29:36.470236Z",
        "servers": null}
        """,
        )

    def get_expected_to_str(self):
        return "abc"
