import json

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.test.client import RequestFactory

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse, patch
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount import providers
from allauth.socialaccount.providers import registry
from allauth.account import app_settings as account_settings
from allauth.account.models import EmailAddress
from allauth.utils import get_user_model

from .provider import FacebookProvider


@override_settings(
    SOCIALACCOUNT_AUTO_SIGNUP=True,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    LOGIN_REDIRECT_URL='/accounts/profile/',
    ACCOUNT_EMAIL_VERIFICATION=account_settings
    .EmailVerificationMethod.NONE,
    SOCIALACCOUNT_PROVIDERS={
        'facebook': {
            'AUTH_PARAMS': {},
            'VERIFIED_EMAIL': False}})
class FacebookTests(create_oauth2_tests(registry.by_id(FacebookProvider.id))):
    facebook_data = """
        {
           "id": "630595557",
           "name": "Raymond Penners",
           "first_name": "Raymond",
           "last_name": "Penners",
           "email": "raymond.penners@gmail.com",
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
        }"""

    def get_mocked_response(self, data=None):
        if data is None:
            data = self.facebook_data
        return MockedResponse(200, data)

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

    def test_username_based_on_provider_with_simple_name(self):
        data = '{"id": "1234567", "name": "Harvey McGillicuddy"}'
        self.login(self.get_mocked_response(data=data))
        socialaccount = SocialAccount.objects.get(uid='1234567')
        self.assertEqual(socialaccount.user.username, 'harvey')

    def test_media_js(self):
        provider = providers.registry.by_id(FacebookProvider.id)
        request = RequestFactory().get(reverse('account_login'))
        request.session = {}
        script = provider.media_js(request)
        self.assertTrue('"appId": "app123id"' in script)

    def test_login_by_token(self):
        resp = self.client.get(reverse('account_login'))
        with patch('allauth.socialaccount.providers.facebook.views'
                   '.requests') as requests_mock:
            mocks = [self.get_mocked_response().json()]
            requests_mock.get.return_value.json \
                = lambda: mocks.pop()
            resp = self.client.post(reverse('facebook_login_by_token'),
                                    data={'access_token': 'dummy'})
            self.assertRedirects(resp, 'http://testserver/accounts/profile/',
                                 fetch_redirect_response=False)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            'facebook': {
                'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
                'VERIFIED_EMAIL': False}})
    def test_login_by_token_reauthenticate(self):
        resp = self.client.get(reverse('account_login'))
        nonce = json.loads(resp.context['fb_data'])['loginOptions']['auth_nonce']
        with patch('allauth.socialaccount.providers.facebook.views'
                   '.requests') as requests_mock:
            mocks = [self.get_mocked_response().json(),
                     {'auth_nonce': nonce}]
            requests_mock.get.return_value.json \
                = lambda: mocks.pop()
            resp = self.client.post(reverse('facebook_login_by_token'),
                                    data={'access_token': 'dummy'})
            self.assertRedirects(resp, 'http://testserver/accounts/profile/',
                                 fetch_redirect_response=False)

    @override_settings(
        SOCIALACCOUNT_PROVIDERS={
            'facebook': {
                'VERIFIED_EMAIL': True}})
    def test_login_verified(self):
        emailaddress = self._login_verified()
        self.assertTrue(emailaddress.verified)

    def test_login_unverified(self):
        emailaddress = self._login_verified()
        self.assertFalse(emailaddress.verified)

    def _login_verified(self):
        resp = self.login(self.get_mocked_response())
        return EmailAddress.objects.get(email='raymond.penners@gmail.com')
