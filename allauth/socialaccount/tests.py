try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
import warnings

from django.test.utils import override_settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import AnonymousUser

from ..tests import MockedResponse, mocked_response
from ..account import app_settings as account_settings
from ..account.models import EmailAddress
from ..account.utils import user_email
from ..utils import get_user_model

from .models import SocialApp, SocialAccount, SocialLogin
from .helpers import complete_social_login


def create_oauth_tests(provider):

    def get_mocked_response(self):
        pass

    def setUp(self):
        app = SocialApp.objects.create(provider=provider.id,
                                       name=provider.id,
                                       key=provider.id,
                                       secret='dummy')
        app.sites.add(Site.objects.get_current())

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        resp_mock = self.get_mocked_response()
        if not resp_mock:
            warnings.warn("Cannot test provider %s, no oauth mock"
                          % self.provider.id)
            return
        resp = self.login(resp_mock)
        self.assertRedirects(resp, reverse('socialaccount_signup'))

    def login(self, resp_mock, process='login'):
        with mocked_response(MockedResponse(200,
                                            'oauth_token=token&'
                                            'oauth_token_secret=psst',
                                            {'content-type':
                                             'text/html'})):
            resp = self.client.get(reverse(self.provider.id + '_login'),
                                   dict(process=process))
        p = urlparse(resp['location'])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id+'_callback')
        self.assertGreater(q['oauth_callback'][0]
                           .find(complete_url), 0)
        with mocked_response(MockedResponse(200,
                                            'oauth_token=token&'
                                            'oauth_token_secret=psst',
                                            {'content-type':
                                             'text/html'}),
                             resp_mock):
            resp = self.client.get(complete_url)
        return resp

    impl = { 'setUp': setUp,
             'login': login,
             'test_login': test_login,
             'get_mocked_response': get_mocked_response }
    class_name = 'OAuth2Tests_'+provider.id
    Class = type(class_name, (TestCase,), impl)
    Class.provider = provider
    return Class


def create_oauth2_tests(provider):

    def get_mocked_response(self):
        pass

    def setUp(self):
        app = SocialApp.objects.create(provider=provider.id,
                                       name=provider.id,
                                       key=provider.id,
                                       secret='dummy')
        app.sites.add(Site.objects.get_current())

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        resp_mock = self.get_mocked_response()
        if not resp_mock:
            warnings.warn("Cannot test provider %s, no oauth mock"
                          % self.provider.id)
            return
        resp = self.login(resp_mock,)
        self.assertRedirects(resp, reverse('socialaccount_signup'))

    def login(self, resp_mock, process='login'):
        resp = self.client.get(reverse(self.provider.id + '_login'),
                               dict(process=process))
        p = urlparse(resp['location'])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id+'_callback')
        self.assertGreater(q['redirect_uri'][0]
                           .find(complete_url), 0)
        with mocked_response(MockedResponse(200,
                                            '{"access_token":"testac"}',
                                            {'content-type':
                                             'application/json'}),
                             resp_mock):
            resp = self.client.get(complete_url,
                                   { 'code': 'test',
                                     'state': q['state'][0] })
        return resp




    impl = { 'setUp': setUp,
             'login': login,
             'test_login': test_login,
             'get_mocked_response': get_mocked_response }
    class_name = 'OAuth2Tests_'+provider.id
    Class = type(class_name, (TestCase,), impl)
    Class.provider = provider
    return Class


class SocialAccountTests(TestCase):

    @override_settings(
        SOCIALACCOUNT_AUTO_SIGNUP=True,
        ACCOUNT_SIGNUP_FORM_CLASS=None,
        ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.NONE
    )

    def test_email_address_created(self):
        factory = RequestFactory()
        request = factory.get('/accounts/login/callback/')
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)

        User = get_user_model()
        user = User()
        setattr(user, account_settings.USER_MODEL_USERNAME_FIELD, 'test')
        setattr(user, account_settings.USER_MODEL_EMAIL_FIELD, 'test@test.com')

        account = SocialAccount(user=user, provider='openid', uid='123')
        sociallogin = SocialLogin(account)
        complete_social_login(request, sociallogin)

        user = User.objects.get(
            **{account_settings.USER_MODEL_USERNAME_FIELD: 'test'}
        )
        self.assertTrue(
            SocialAccount.objects.filter(user=user, uid=account.uid).exists()
        )
        self.assertTrue(
            EmailAddress.objects.filter(user=user, email=user_email(user)).exists()
        )
