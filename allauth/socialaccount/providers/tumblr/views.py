import json

from django.utils import six

from allauth.socialaccount import providers
from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)

from .provider import TumblrProvider


class TumblrAPI(OAuth):
    url = 'http://api.tumblr.com/v2/user/info'

    def get_user_info(self):
        try:
            return json.loads(self.query(self.url))['response']['user']
        except:
            return None


class TumblrOAuthAdapter(OAuthAdapter):
    provider_id = TumblrProvider.id
    request_token_url = 'https://www.tumblr.com/oauth/request_token'
    access_token_url = 'https://www.tumblr.com/oauth/access_token'
    authorize_url = 'https://www.tumblr.com/oauth/authorize'

    def complete_login(self, request, app, token):
        client = TumblrAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)

oauth_login = OAuthLoginView.adapter_view(TumblrOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TumblrOAuthAdapter)
