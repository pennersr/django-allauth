from xml.etree import ElementTree
from xml.parsers.expat import ExpatError

from django.utils import six

from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)

from .provider import FlickrProvider

import json
import urllib

class FlickrAPI(OAuth):

    login_url= 'http://api.flickr.com/services/rest?nojsoncallback=1&format=json'
    info_url = 'http://api.flickr.com/services/rest?nojsoncallback=1&format=json&method=flickr.people.getInfo'

    def get_user_info(self):
        p = { 'method': 'flickr.test.login' }
        u = json.loads(self.query(self.login_url + '&' +  urllib.urlencode(p)))

        p = { 'method': 'flickr.people.getInfo', 'user_id' : u['user']['id'] }
        user = json.loads(self.query(self.info_url + '&' + urllib.urlencode(p)))
        return user
    
class FlickrOAuthAdapter(OAuthAdapter):
    provider_id = FlickrProvider.id
    request_token_url = 'http://www.flickr.com/services/oauth/request_token'
    access_token_url = 'http://www.flickr.com/services/oauth/access_token'
    authorize_url = 'http://www.flickr.com/services/oauth/authorize'

    def complete_login(self, request, app, token):
        client = FlickrAPI(request, app.client_id, app.secret,
                             self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

oauth_login = OAuthLoginView.adapter_view(FlickrOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(FlickrOAuthAdapter)
