import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.adapter import get_adapter

from .provider import SoundCloudProvider

class SoundCloudOAuth2Adapter(OAuth2Adapter):
    provider_id = SoundCloudProvider.id
    access_token_url = 'https://api.soundcloud.com/oauth2/token'
    authorize_url = 'https://soundcloud.com/connect'
    profile_url = 'https://api.soundcloud.com/me.json'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={ 'oauth_token': token.token })
        extra_data = resp.json()
        uid = str(extra_data['id'])
        user = get_adapter() \
            .populate_new_user(name=extra_data.get('full_name'),
                               username=extra_data.get('username'),
                               email=extra_data.get('email'))
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)

oauth2_login = OAuth2LoginView.adapter_view(SoundCloudOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SoundCloudOAuth2Adapter)

