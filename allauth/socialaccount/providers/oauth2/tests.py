# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import json, re, sys

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, NoReverseMatch, clear_url_caches, set_urlconf
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.utils.http import urlquote_plus as urlquote, urlunquote_plus as urlunquote

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

from allauth.account import app_settings as account_settings
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers import registry
from allauth.socialaccount.providers.fake.views import FakeOAuth2Adapter
from allauth.socialaccount.tests import create_oauth2_tests
from allauth.tests import MockedResponse
from allauth.utils import get_current_site

from requests.exceptions import HTTPError

from .views import OAuth2Adapter, OAuth2LoginView, proxy_login_callback, MissingParameter


class OAuth2Tests(TestCase):
    def param(self, param, url):
        # Look for a redirect uri
        url = urlunquote(url)
        m = re.match('.*%s=(.*?)[|&.*]' % param, url)
        if m is None:
            return ''
        return m.group(1)

    def init_request(self, endpoint, params):
        self.request = RequestFactory().get(reverse(endpoint), params)
        SessionMiddleware().process_request(self.request)

    def setUp(self):
        app = SocialApp.objects.create(provider=FakeOAuth2Adapter.provider_id,
                                       name=FakeOAuth2Adapter.provider_id,
                                       client_id='app123id',
                                       key=FakeOAuth2Adapter.provider_id,
                                       secret='dummy')
        app.sites.add(get_current_site())


class OAuth2TestsNoProxying(OAuth2Tests):
    def setUp(self):
        self.init_request('fake_login', dict(process='login'))
        super(OAuth2TestsNoProxying, self).setUp()

    def test_proxyless_login(self):
        login_view = OAuth2LoginView.adapter_view(FakeOAuth2Adapter)
        login_response = login_view(self.request)
        self.assertEqual(login_response.status_code, 302)  # Redirect
        self.assertEqual(self.param('redirect_uri', login_response['location']),
                         'http://testserver/fake/login/callback/')

    def test_is_not_login_proxy(self):
        with self.assertRaises(NoReverseMatch):
            reverse('fake_proxy')


@override_settings(ACCOUNT_LOGIN_CALLBACK_PROXY='https://loginproxy')
class OAuth2TestsUsesProxy(OAuth2Tests):
    def setUp(self):
        self.init_request('fake_login', dict(process='login'))
        super(OAuth2TestsUsesProxy, self).setUp()

    def test_login_by_proxy(self):
        login_view = OAuth2LoginView.adapter_view(FakeOAuth2Adapter)
        login_response = login_view(self.request)
        self.assertEqual(login_response.status_code, 302)  # Redirect
        self.assertEqual(self.param('redirect_uri', login_response['location']),
                         'https://loginproxy/fake/login/callback/proxy/')
        state = json.loads(self.param('state', login_response['location']))
        self.assertEqual(state['host'], 'http://testserver/fake/login/')

    def test_is_not_login_proxy(self):
        with self.assertRaises(NoReverseMatch):
            reverse('fake_proxy')


@override_settings(
    ACCOUNT_LOGIN_PROXY_REDIRECT_WHITELIST=
    'https://cheshirecat,https://tweedledee,',
    ACCOUNT_LOGIN_PROXY_REDIRECT_DOMAIN_WHITELIST=
    'sub.domain.com,'
)
class OAuth2TestsIsProxy(OAuth2Tests):
    def reload_urls(self):
        for module in sys.modules:
            if module.endswith('urls'):
                reload(sys.modules[module])
        clear_url_caches()


    def setUp(self):
        super(OAuth2TestsIsProxy, self).setUp()
        self.reload_urls()

    @override_settings(ACCOUNT_LOGIN_PROXY_REDIRECT_WHITELIST='')
    def tearDown(self):
        super(OAuth2TestsIsProxy, self).tearDown()
        self.reload_urls()

    def tests_is_login_proxy(self):
        reverse('fake_proxy')

    def test_rejects_request_with_no_host_in_state(self):
        self.init_request('fake_proxy', dict(process='login'))
        with self.assertRaises(MissingParameter):
            proxy_login_callback(
                self.request, callback_view_name='fake_callback')

    def test_rejects_request_with_unwhitelisted_host(self):
        state = {'host': 'https://bar.domain.com'}
        self.init_request(
            'fake_proxy', dict(process='login', state=json.dumps(state)))
        with self.assertRaises(PermissionDenied):
            proxy_login_callback(
                self.request, callback_view_name='fake_callback')

    def tests_redirects_request_with_whitelisted_host(self):
        state = {'host': 'https://tweedledee'}
        serialized_state = json.dumps(state)
        self.init_request(
            'fake_proxy', dict(process='login', state=serialized_state))
        proxy_response = proxy_login_callback(
            self.request, callback_view_name='fake_callback')
        self.assertEqual(proxy_response.status_code, 302)  # Redirect
        self.assertEqual(
            proxy_response['location'],
            ('https://tweedledee/fake/login/callback/'
            '?process=login&state=%s' % urlquote(serialized_state)))

    def tests_redirects_request_with_domain_whitelisted_host(self):
        state = {'host': 'https://foo.sub.domain.com'}
        serialized_state = json.dumps(state)
        self.init_request(
            'fake_proxy', dict(process='login', state=serialized_state))
        proxy_response = proxy_login_callback(
            self.request, callback_view_name='fake_callback')
        self.assertEqual(proxy_response.status_code, 302)  # Redirect
        self.assertEqual(
            proxy_response['location'],
            ('https://foo.sub.domain.com/fake/login/callback/'
            '?process=login&state=%s' % urlquote(serialized_state)))

    def test_rejects_request_with_scheme_mismatch(self):
        state = {'host': 'ftp://tweedledee'}
        self.init_request(
            'fake_proxy', dict(process='login', state=json.dumps(state)))
        with self.assertRaises(PermissionDenied):
            proxy_login_callback(
                self.request, callback_view_name='fake_callback')

    def test_rejects_request_with_whitelisted_prefix(self):
        state = {'host': 'https://tweedledee.creds4u.biz'}
        self.init_request(
            'fake_proxy', dict(process='login', state=json.dumps(state)))
        with self.assertRaises(PermissionDenied):
            proxy_login_callback(
                self.request, callback_view_name='fake_callback')
