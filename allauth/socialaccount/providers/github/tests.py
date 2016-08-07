from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase
from allauth.socialaccount.models import SocialAccount

from .provider import GitHubProvider


class GitHubTests(OAuth2TestsMixin, TestCase):
    provider_id = GitHubProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "type":"User",
            "organizations_url":"https://api.github.com/users/pennersr/orgs",
            "gists_url":"https://api.github.com/users/pennersr/gists{/gist_id}",
            "received_events_url":"https://api.github.com/users/pennersr/received_events",
            "gravatar_id":"8639768262b8484f6a3380f8db2efa5b",
            "followers":16,
            "blog":"http://www.intenct.info",
            "avatar_url":"https://secure.gravatar.com/avatar/8639768262b8484f6a3380f8db2efa5b?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png",
            "login":"pennersr",
            "created_at":"2010-02-10T12:50:51Z",
            "company":"IntenCT",
            "subscriptions_url":"https://api.github.com/users/pennersr/subscriptions",
            "public_repos":14,
            "hireable":false,
            "url":"https://api.github.com/users/pennersr",
            "public_gists":0,
            "starred_url":"https://api.github.com/users/pennersr/starred{/owner}{/repo}",
            "html_url":"https://github.com/pennersr",
            "location":"The Netherlands",
            "bio":null,
            "name":"Raymond Penners",
            "repos_url":"https://api.github.com/users/pennersr/repos",
            "followers_url":"https://api.github.com/users/pennersr/followers",
            "id":201022,
            "following":0,
            "email":"raymond.penners@intenct.nl",
            "events_url":"https://api.github.com/users/pennersr/events{/privacy}",
            "following_url":"https://api.github.com/users/pennersr/following"
        }""")

    def test_account_name_null(self):
        """String conversion when GitHub responds with empty name"""
        data = """{
            "type": "User",
            "id": 201022,
            "login": "pennersr",
            "name": null
        }"""
        self.login(MockedResponse(200, data))
        socialaccount = SocialAccount.objects.get(uid='201022')
        self.assertIsNone(socialaccount.extra_data.get('name'))
        account = socialaccount.get_provider_account()
        self.assertIsNotNone(account.to_str())
        self.assertEqual(account.to_str(), 'pennersr')
