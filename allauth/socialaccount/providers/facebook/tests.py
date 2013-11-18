from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount import providers
from allauth.socialaccount.providers import registry
from allauth.utils import get_user_model
from django.test.client import RequestFactory

from .provider import FacebookProvider


class FacebookTests(create_oauth2_tests(registry.by_id(FacebookProvider.id))):
    def get_mocked_response(self):
        return MockedResponse(200, """
        {
           "id": "630595557",
           "name": "Raymond Penners",
           "first_name": "Raymond",
           "last_name": "Penners",
           "link": "https://www.facebook.com/raymond.penners",
           "username": "raymond.penners",
           "birthday": "07/17/1973",
           "work": [
              {
                 "employer": {
                    "id": "204953799537777",
                    "name": "IntenCT"
                 }
              }
           ],
           "timezone": 1,
           "locale": "nl_NL",
           "verified": true,
           "updated_time": "2012-11-30T20:40:33+0000"
        }""")

    def test_username_conflict(self):
        User = get_user_model()
        User.objects.create(username='raymond.penners')
        self.login(self.get_mocked_response())
        socialaccount = SocialAccount.objects.get(uid='630595557')
        self.assertEqual(socialaccount.user.username, 'raymond')

    def test_username_based_on_provider(self):
        self.login(self.get_mocked_response())
        socialaccount = SocialAccount.objects.get(uid='630595557')
        self.assertEqual(socialaccount.user.username, 'raymond.penners')

    def test_media_js(self):
        provider = providers.registry.by_id(FacebookProvider.id)
        request = RequestFactory().get('/accounts/login/')
        script = provider.media_js(request)
        self.assertTrue("appId: 'app123id'" in script)
