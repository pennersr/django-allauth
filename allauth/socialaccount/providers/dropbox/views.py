import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)

from .provider import DropboxProvider


class DropboxAPI(OAuth):
    """
    Verifying twitter credentials
    """
    url = 'https://api.dropbox.com/1/account/info'

    def get_user_info(self):
        user = json.loads(self.query(self.url))
        return user


class DropboxOAuthAdapter(OAuthAdapter):
    provider_id = DropboxProvider.id
    request_token_url = 'https://api.dropbox.com/1/oauth/request_token'
    access_token_url = 'https://api.dropbox.com/1/oauth/access_token'
    authorize_url = 'https://www.dropbox.com/1/oauth/authorize'

    def complete_login(self, request, app, token, response):
        client = DropboxAPI(request, app.client_id, app.secret,
                            self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth_login = OAuthLoginView.adapter_view(DropboxOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(DropboxOAuthAdapter)
