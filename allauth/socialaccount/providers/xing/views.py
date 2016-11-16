import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)

from .provider import XingProvider


class XingAPI(OAuth):
    url = 'https://api.xing.com/v1/users/me.json'

    def get_user_info(self):
        user = json.loads(self.query(self.url))
        return user


class XingOAuthAdapter(OAuthAdapter):
    provider_id = XingProvider.id
    request_token_url = 'https://api.xing.com/v1/request_token'
    access_token_url = 'https://api.xing.com/v1/access_token'
    authorize_url = 'https://www.xing.com/v1/authorize'

    def complete_login(self, request, app, token, response):
        client = XingAPI(request, app.client_id, app.secret,
                         self.request_token_url)
        extra_data = client.get_user_info()['users'][0]
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth_login = OAuthLoginView.adapter_view(XingOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(XingOAuthAdapter)
