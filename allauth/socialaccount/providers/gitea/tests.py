from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import GiteaProvider


class GiteaTests(OAuth2TestsMixin, TestCase):
    provider_id = GiteaProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
            {
                "id": 4940,
                "login": "giteauser",
                "full_name": "",
                "email": "giteauser@example.com",
                "avatar_url": "https://gitea.com/user/avatar/giteauser/-1",
                "language": "en-US",
                "is_admin": true,
                "last_login": "2021-08-20T20:07:39Z",
                "created": "2018-05-03T16:04:34Z",
                "restricted": false,
                "active": true,
                "prohibit_login": false,
                "location": "",
                "website": "",
                "description": "",
                "visibility": "public",
                "followers_count": 0,
                "following_count": 0,
                "starred_repos_count": 0,
                "username": "giteauser"
            }""",
        )

    def get_expected_to_str(self):
        return "giteauser"

    def test_account_name_null(self):
        """String conversion when Gitea responds with empty username"""
        data = """{
            "id": 4940,
            "login": "giteauser",
            "username": null
        }"""
        self.login(MockedResponse(200, data))
        socialaccount = SocialAccount.objects.get(uid="4940")
        self.assertIsNone(socialaccount.extra_data.get("name"))
        account = socialaccount.get_provider_account()
        self.assertIsNotNone(account.to_str())
        self.assertEqual(account.to_str(), "giteauser")
