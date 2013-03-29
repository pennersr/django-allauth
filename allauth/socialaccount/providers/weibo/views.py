import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.adapter import get_adapter

from .provider import WeiboProvider

class WeiboOAuth2Adapter(OAuth2Adapter):
    provider_id = WeiboProvider.id
    access_token_url = 'https://api.weibo.com/oauth2/access_token'
    authorize_url = 'https://api.weibo.com/oauth2/authorize'
    profile_url = 'https://api.weibo.com/2/users/show.json'

    def complete_login(self, request, app, token, **kwargs):
        uid = kwargs.get('response', {}).get('uid')
        resp = requests.get(self.profile_url,
                            params={ 'access_token': token.token,
                                     'uid': uid })
        extra_data = resp.json()
        user = get_adapter() \
            .populate_new_user(username=extra_data.get('screen_name'),
                               name=extra_data.get('name'))
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(WeiboOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WeiboOAuth2Adapter)

