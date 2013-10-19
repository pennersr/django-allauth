from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.providers import registry

from .provider import AngelListProvider


class AngelListTests(create_oauth2_tests(registry
                                         .by_id(AngelListProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
{"name":"pennersr","id":424732,"bio":"","follower_count":0,
"angellist_url":"https://angel.co/dsxtst",
"image":"https://angel.co/images/shared/nopic.png",
"email":"raymond.penners@gmail.com","blog_url":null,
"online_bio_url":null,"twitter_url":"https://twitter.com/dsxtst",
"facebook_url":null,"linkedin_url":null,"aboutme_url":null,
"github_url":null,"dribbble_url":null,"behance_url":null,
"what_ive_built":null,"locations":[],"roles":[],"skills":[],
"investor":false,"scopes":["message","talent","dealflow","comment",
"email"]}
""")
