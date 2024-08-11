from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from .provider import AngelListProvider


class AngelListTests(OAuth2TestsMixin, TestCase):
    provider_id = AngelListProvider.id

    def get_mocked_response(self):
        return MockedResponse(
            200,
            """
{"name":"pennersr","id":424732,"bio":"","follower_count":0,
"angellist_url":"https://angel.co/dsxtst",
"image":"https://angel.co/images/shared/nopic.png",
"email":"raymond.penners@example.com","blog_url":null,
"online_bio_url":null,"twitter_url":"https://twitter.com/dsxtst",
"facebook_url":null,"linkedin_url":null,"aboutme_url":null,
"github_url":null,"dribbble_url":null,"behance_url":null,
"what_ive_built":null,"locations":[],"roles":[],"skills":[],
"investor":false,"scopes":["message","talent","dealflow","comment",
"email"]}
""",
        )

    def get_expected_to_str(self):
        return "raymond.penners@example.com"
