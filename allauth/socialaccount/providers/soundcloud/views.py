from django.contrib.auth.models import User

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount import requests

from allauth.socialaccount.models import SocialAccount, SocialLogin

from provider import SoundCloudProvider


class SoundCloudOAuth2Adapter(OAuth2Adapter):
    provider_id = SoundCloudProvider.id
    access_token_url = 'https://api.soundcloud.com/oauth2/token'
    authorize_url = 'https://soundcloud.com/connect'
    profile_url = 'https://api.soundcloud.com/me.json'

    def complete_login(self, request, app, token):
        resp = requests.get(self.profile_url,
                            params={ 'oauth_token': token.token })
        extra_data = resp.json
        uid = str(extra_data['id'])
        name_parts = extra_data.get('full_name', '').split(' ', 1)
        if len(name_parts) == 2:
            first_name, last_name = name_parts
        else:
            first_name, last_name = name_parts[0], ''
        user_kwargs = {'first_name': first_name, 
                       'last_name': last_name}
        user = User(username=extra_data.get('username', ''),
                    email=extra_data.get('email', ''),
                    **user_kwargs)
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)

oauth2_login = OAuth2LoginView.adapter_view(SoundCloudOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SoundCloudOAuth2Adapter)

