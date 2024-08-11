import json

from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.gitlab.provider import GitLabProvider
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .views import _check_errors


class GitLabTests(OAuth2TestsMixin, TestCase):
    provider_id = GitLabProvider.id
    _uid = 2

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "avatar_url": "https://secure.gravatar.com/avatar/123",
                "bio": null,
                "can_create_group": true,
                "can_create_project": true,
                "color_scheme_id": 5,
                "confirmed_at": "2015-03-02T16:53:58.370Z",
                "created_at": "2015-03-02T16:53:58.885Z",
                "current_sign_in_at": "2018-06-12T18:44:49.985Z",
                "email": "mr.bob@gitlab.example.com",
                "external": false,
                "id": 2,
                "identities": [],
                "last_activity_on": "2018-06-11",
                "last_sign_in_at": "2018-05-31T14:59:44.527Z",
                "linkedin": "",
                "location": null,
                "name": "Mr Bob",
                "organization": null,
                "projects_limit": 10,
                "shared_runners_minutes_limit": 2000,
                "skype": "",
                "state": "active",
                "theme_id": 6,
                "twitter": "mrbob",
                "two_factor_enabled": true,
                "username": "mr.bob",
                "web_url": "https://gitlab.example.com/u/mr.bob",
                "website_url": ""
            }
        """,
        )

    def get_expected_to_str(self):
        return "mr.bob"

    def test_valid_response(self):
        data = {"id": 12345}
        response = MockedResponse(200, json.dumps(data))
        self.assertEqual(_check_errors(response), data)

    def test_invalid_data(self):
        response = MockedResponse(200, json.dumps({}))
        with self.assertRaises(OAuth2Error):
            # No id, raises
            _check_errors(response)

    def test_account_invalid_response(self):
        body = (
            "403 Forbidden  - You (@domain.com) must accept the Terms of "
            "Service in order to perform this action. Please access GitLab "
            "from a web browser to accept these terms."
        )
        response = MockedResponse(403, body)

        # GitLab allow users to login with their API and provides
        # an error requiring the user to accept the Terms of Service.
        # see: https://gitlab.com/gitlab-org/gitlab-foss/-/issues/45849
        with self.assertRaises(OAuth2Error):
            # no id, 4xx code, raises
            _check_errors(response)

    def test_error_response(self):
        body = "403 Forbidden"
        response = MockedResponse(403, body)

        with self.assertRaises(OAuth2Error):
            # no id, 4xx code, raises
            _check_errors(response)

    def test_invalid_response(self):
        response = MockedResponse(200, json.dumps({}))
        with self.assertRaises(OAuth2Error):
            # No id, raises
            _check_errors(response)

    def test_bad_response(self):
        response = MockedResponse(400, json.dumps({}))
        with self.assertRaises(OAuth2Error):
            # bad json, raises
            _check_errors(response)

    def test_extra_data(self):
        self.login(self.get_mocked_response())
        account = SocialAccount.objects.get(uid=str(self._uid))
        self.assertEqual(account.extra_data["id"], self._uid)
