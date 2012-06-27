import urlparse

from datetime import timedelta, datetime

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core import mail
from django.contrib.sites.models import Site

import providers

from providers.oauth2.models import OAuth2Provider
from models import SocialApp

def create_oauth2_tests(provider):
    def setUp(self):
        self.app = SocialApp.objects.create(site=Site.objects.get_current(),
                                            provider=self.provider.id,
                                            name='oauth2 test',
                                            key='123',
                                            secret='abc')

    def test_login(self):
        resp = self.client.get(reverse(self.provider.id + '_login'))
        p = urlparse.urlparse(resp['location'])
        q = urlparse.parse_qs(p.query)
        complete_url = reverse(self.provider.id+'_callback')
        self.assertGreater(q['redirect_uri'][0]
                           .find(complete_url), 0)
        resp = self.client.get(complete_url,
                               { 'code': 'test' })


    
    impl = { 'setUp': setUp,
             'test_login': test_login }
    class_name = 'OAuth2Tests_'+provider.id
    Class = type(class_name, (TestCase,), impl)
    globals()[class_name] = Class
    Class.provider = provider

for provider in providers.registry.get_list():
    if isinstance(provider,OAuth2Provider):
        create_oauth2_tests(provider)

