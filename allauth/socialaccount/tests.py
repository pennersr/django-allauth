import urlparse
import warnings

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.test.utils import override_settings

import providers
from allauth.tests import MockedResponse, mocked_response

from providers.oauth2.provider import OAuth2Provider

from models import SocialApp

def create_oauth2_tests(provider):

    def get_mocked_response(self):
        pass

    def setUp(self):
        for provider in providers.registry.get_list():
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

    def login(self, resp_mock):
        resp = self.client.get(reverse(self.provider.id + '_login'))
        p = urlparse.urlparse(resp['location'])
        q = urlparse.parse_qs(p.query)
        complete_url = reverse(self.provider.id+'_callback')
        self.assertGreater(q['redirect_uri'][0]
                           .find(complete_url), 0)
        with mocked_response(MockedResponse(200,
                                            '{"access_token":"testac"}',
                                            {'content-type':
                                             'application/json'}),
                             resp_mock):
            resp = self.client.get(complete_url,
                                   { 'code': 'test' })
        return resp




    impl = { 'setUp': setUp,
             'login': login,
             'test_login': test_login,
             'get_mocked_response': get_mocked_response }
    class_name = 'OAuth2Tests_'+provider.id
    Class = type(class_name, (TestCase,), impl)
    Class.provider = provider
    return Class
