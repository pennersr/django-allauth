import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (OAuthAdapter,
                                                         OAuthLoginView,
                                                         OAuthCallbackView)
from allauth.socialaccount.models import SocialLogin, SocialAccount
from allauth.socialaccount.adapter import get_adapter

from provider import DropboxProvider

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

    def complete_login(self, request, app, token):
        client = DropboxAPI(request, app.client_id, app.secret,
                            self.request_token_url)
        extra_data = client.get_user_info()
        uid = extra_data['uid']
        user = get_adapter() \
            .populate_new_user(username=extra_data.get('display_name'),
                               name=extra_data.get('display_name'),
                               email=extra_data.get('email'))
        account = SocialAccount(user=user,
                                uid=uid,
                                provider=DropboxProvider.id,
                                extra_data=extra_data)
        return SocialLogin(account)


oauth_login = OAuthLoginView.adapter_view(DropboxOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(DropboxOAuthAdapter)

