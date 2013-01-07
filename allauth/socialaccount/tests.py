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
    'github': MockedResponse(200, """
{"type":"User","organizations_url":"https://api.github.com/users/pennersr/orgs","gists_url":"https://api.github.com/users/pennersr/gists{/gist_id}","received_events_url":"https://api.github.com/users/pennersr/received_events","gravatar_id":"8639768262b8484f6a3380f8db2efa5b","followers":16,"blog":"http://www.intenct.info","avatar_url":"https://secure.gravatar.com/avatar/8639768262b8484f6a3380f8db2efa5b?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png","login":"pennersr","created_at":"2010-02-10T12:50:51Z","company":"IntenCT","subscriptions_url":"https://api.github.com/users/pennersr/subscriptions","public_repos":14,"hireable":false,"url":"https://api.github.com/users/pennersr","public_gists":0,"starred_url":"https://api.github.com/users/pennersr/starred{/owner}{/repo}","html_url":"https://github.com/pennersr","location":"The Netherlands","bio":null,"name":"Raymond Penners","repos_url":"https://api.github.com/users/pennersr/repos","followers_url":"https://api.github.com/users/pennersr/followers","id":201022,"following":0,"email":"raymond.penners@intenct.nl","events_url":"https://api.github.com/users/pennersr/events{/privacy}","following_url":"https://api.github.com/users/pennersr/following"}
"""),
    'facebook': MockedResponse(200, """
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
}
"""),
    'soundcloud': MockedResponse(200, """
{"website": null, "myspace_name": null, "public_favorites_count": 0, "followings_count": 1, "full_name": "", "id": 22341947, "city": null, "track_count": 0, "playlist_count": 0, "discogs_name": null, "private_tracks_count": 0, "followers_count": 0, "online": true, "username": "user187631676", "description": null, "kind": "user", "website_title": null, "primary_email_confirmed": false, "permalink_url": "http://soundcloud.com/user187631676", "private_playlists_count": 0, "permalink": "user187631676", "country": null, "uri": "https://api.soundcloud.com/users/22341947", "avatar_url": "https://a1.sndcdn.com/images/default_avatar_large.png?4b4189b", "plan": "Free"}
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
        resp_mock = mocked_oauth_responses.get(self.provider.id)
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
             'test_login': test_login }
    class_name = 'OAuth2Tests_'+provider.id
    Class = type(class_name, (TestCase,), impl)
    Class.provider = provider
    return Class

# FIXME: Move tests to provider specific app (as has been done for Google)
for provider in providers.registry.get_list():
    if isinstance(provider,OAuth2Provider):
        if provider.id != 'google':
            Class = create_oauth2_tests(provider)
            globals()[Class.__name__] = Class

