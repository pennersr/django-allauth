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


mocked_oauth_responses = {
    'google': MockedResponse(200, """
{"family_name": "Penners", "name": "Raymond Penners", 
               "picture": "https://lh5.googleusercontent.com/-GOFYGBVOdBQ/AAAAAAAAAAI/AAAAAAAAAGM/WzRfPkv4xbo/photo.jpg", 
               "locale": "nl", "gender": "male", 
               "email": "raymond.penners@gmail.com", 
               "link": "https://plus.google.com/108204268033311374519", 
               "given_name": "Raymond", "id": "108204268033311374519", 
                "verified_email": true}
"""),
    'stackexchange': MockedResponse(200, """
{"has_more": false, "items": [{"is_employee": false, "last_access_date": 1356200390, "display_name": "pennersr", "account_id": 291652, "badge_counts": {"bronze": 2, "silver": 2, "gold": 0}, "last_modified_date": 1356199552, "profile_image": "http://www.gravatar.com/avatar/053d648486d567d3143d6bad8df8cfeb?d=identicon&r=PG", "user_type": "registered", "creation_date": 1296223711, "reputation_change_quarter": 148, "reputation_change_year": 378, "reputation": 504, "link": "http://stackoverflow.com/users/593944/pennersr", "reputation_change_week": 0, "user_id": 593944, "reputation_change_month": 10, "reputation_change_day": 0}], "quota_max": 10000, "quota_remaining": 9999}
""") }


def create_oauth2_tests(provider):
    def setUp(self):
        for provider in providers.registry.get_list():
            app = SocialApp.objects.create(provider=provider.id,
                                           name=provider.id,
                                           key=provider.id,
                                           secret='dummy')
            app.sites.add(Site.objects.get_current())

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
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
        with mocked_response(MockedResponse(200,
                                            '{"access_token":"testac"}',
                                            {'content-type': 
                                             'application/json'}),
                             resp_mock):
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

