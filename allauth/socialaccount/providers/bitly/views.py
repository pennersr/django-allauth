import requests

from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import BitlyProvider

class BitlyOAuth2Adapter(OAuth2Adapter):
    provider_id = BitlyProvider.id
    access_token_url = 'https://api-ssl.bitly.com/oauth/access_token'
    authorize_url = 'https://bitly.com/oauth/authorize'
    profile_url = 'https://api-ssl.bitly.com/v3/user/info'
    supports_state = False

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={ 'access_token': token.token }
        )
        extra_data = resp.json()['data']
        uid = str(extra_data['login'])
        user = get_adapter().populate_new_user(
            username=extra_data['login'],
            name=extra_data.get('full_name')
        )
        account = SocialAccount(
            user=user,
            uid=uid,
            extra_data=extra_data,
            provider=self.provider_id
        )
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(BitlyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BitlyOAuth2Adapter)

