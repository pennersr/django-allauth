import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from .provider import VimeoProvider


class VimeoAPI(OAuth):
    url = 'http://vimeo.com/api/rest/v2?method=vimeo.people.getInfo'

    def get_user_info(self):
        url = self.url
        data = json.loads(self.query(url, params=dict(format='json')))
        return data['person']


class VimeoOAuthAdapter(OAuthAdapter):
    provider_id = VimeoProvider.id
    request_token_url = 'https://vimeo.com/oauth/request_token'
    access_token_url = 'https://vimeo.com/oauth/access_token'
    authorize_url = 'https://vimeo.com/oauth/authorize'

    def complete_login(self, request, app, token, response):
        client = VimeoAPI(request, app.client_id, app.secret,
                          self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth_login = OAuthLoginView.adapter_view(VimeoOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(VimeoOAuthAdapter)
