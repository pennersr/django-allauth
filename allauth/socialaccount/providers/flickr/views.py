import json
from django.utils.http import urlencode

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthLoginView,
    OAuthCallbackView)

from .provider import FlickrProvider


class FlickrAPI(OAuth):

    api_url = 'https://api.flickr.com/services/rest'

    def get_user_info(self):
        default_params = {'nojsoncallback': '1',
                          'format': 'json'}
        p = dict({'method': 'flickr.test.login'},
                 **default_params)
        u = json.loads(self.query(self.api_url + '?' + urlencode(p)))

        p = dict({'method': 'flickr.people.getInfo',
                  'user_id': u['user']['id']},
                 **default_params)
        user = json.loads(
            self.query(self.api_url + '?' + urlencode(p)))
        return user


class FlickrOAuthAdapter(OAuthAdapter):
    provider_id = FlickrProvider.id
    request_token_url = 'http://www.flickr.com/services/oauth/request_token'
    access_token_url = 'http://www.flickr.com/services/oauth/access_token'
    authorize_url = 'http://www.flickr.com/services/oauth/authorize'

    def complete_login(self, request, app, token, response):
        client = FlickrAPI(request, app.client_id, app.secret,
                           self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

oauth_login = OAuthLoginView.adapter_view(FlickrOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(FlickrOAuthAdapter)
