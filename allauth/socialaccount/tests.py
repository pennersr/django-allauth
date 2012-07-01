import urlparse
import warnings

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

import providers
from allauth.socialaccount import requests

from providers.oauth2.provider import OAuth2Provider

from models import SocialApp


mocked_oauth_responses = {
    'google': requests.Response(200, """
{"family_name": "Penners", "name": "Raymond Penners", 
               "picture": "https://lh5.googleusercontent.com/-GOFYGBVOdBQ/AAAAAAAAAAI/AAAAAAAAAGM/WzRfPkv4xbo/photo.jpg", 
               "locale": "nl", "gender": "male", 
               "email": "raymond.penners@gmail.com", 
               "link": "https://plus.google.com/108204268033311374519", 
               "given_name": "Raymond", "id": "108204268033311374519", 
                "verified_email": true}
""")
}

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
        resp_mock = mocked_oauth_responses.get(self.provider.id)
        if not resp_mock:
            warnings.warn("Cannot test provider %s, no oauth mock" 
                          % self.provider.id)
            return
        requests.mock_next_request \
            (requests.Response(200,
                               '{"access_token":"testac"}',
                               {'content-type': 
                                'application/json'}))
        requests.mock_next_request(resp_mock)
        resp = self.client.get(complete_url,
                               { 'code': 'test' })
        self.assertRedirects(resp, reverse('socialaccount_signup'))

    
    impl = { 'setUp': setUp,
             'test_login': test_login }
    class_name = 'OAuth2Tests_'+provider.id
    Class = type(class_name, (TestCase,), impl)
    globals()[class_name] = Class
    Class.provider = provider

for provider in providers.registry.get_list():
    if isinstance(provider,OAuth2Provider):
        create_oauth2_tests(provider)

