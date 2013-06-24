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

    def get_login_response_json(self):
        return ('{'
            '"uid":"weibo", '
            '"access_token":"testac", '
            '"refresh_token":"testrf"'
        '}')

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

    def test_account_tokens(self, multiple_login=False):
        email = 'some@mail.com'
        user = get_user_model().objects.create(username='user',
                                   is_active=True,
                                   email=email)
        user.set_password('test')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email=email,
                                    primary=True,
                                    verified=True)
        self.client.login(username=user.username,
                          password='test')
        self.login(self.get_mocked_response(), process='connect')
        if multiple_login:
            glr = self.get_login_response_json
            self.get_login_response_json = (
                lambda *args: '{"uid":"weibo","access_token":"testac"}')
            try:
                self.login(
                    self.get_mocked_response(),
                    process='connect')
            finally:
                self.get_login_response_json = glr
        # get account
        sa = SocialAccount.objects.filter(user=user, provider=self.provider.id).get()
        # get token
        t = sa.socialtoken_set.get()
        # verify access_token and refresh_token
        self.assertEquals('testac', t.token)
        self.assertEquals('testrf', t.token_secret)

    def test_account_refresh_token_saved_next_login(self):
        '''
        fails if a login missing a refresh token, deletes the previously
        saved refresh token. Systems such as google's oauth only send
        a refresh token on first login.
        '''
        self.test_account_tokens(multiple_login=True)

    def login(self, resp_mock, process='login'):
        resp = self.client.get(reverse(self.provider.id + '_login'),
                               dict(process=process))
        p = urlparse(resp['location'])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id+'_callback')
        self.assertGreater(q['redirect_uri'][0]
                           .find(complete_url), 0)
        response_json = self.get_login_response_json()
        with mocked_response(
                MockedResponse(
                    200,
                    response_json,
                    {'content-type': 'application/json'}),
                resp_mock):
            resp = self.client.get(complete_url,
                                   { 'code': 'test',
                                     'state': q['state'][0] })
        return resp




    impl = { 'setUp': setUp,
             'login': login,
             'test_login': test_login,
             'test_account_tokens': test_account_tokens,
             'test_account_refresh_token_saved_next_login': test_account_refresh_token_saved_next_login,
             'get_login_response_json': get_login_response_json,
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
