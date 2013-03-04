import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.adapter import get_adapter

from provider import TwitchProvider

class TwitchOAuth2Adapter(OAuth2Adapter):
    provider_id = TwitchProvider.id
    access_token_url = 'https://api.twitch.tv/kraken/oauth2/token'
    authorize_url = 'https://api.twitch.tv/kraken/oauth2/authorize'
    profile_url = 'https://api.twitch.tv/kraken/user'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={ 'oauth_token': token.token })
        extra_data = resp.json()
        uid = str(extra_data['_id'])
        user = get_adapter() \
            .populate_new_user(username=extra_data.get('display_name'),
                               name=extra_data.get('name'),
                               email=extra_data.get('email'))
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(TwitchOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TwitchOAuth2Adapter)

