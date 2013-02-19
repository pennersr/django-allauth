import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.providers import registry
from allauth.socialaccount.adapter import get_adapter

from provider import StackExchangeProvider

class StackExchangeOAuth2Adapter(OAuth2Adapter):
    provider_id = StackExchangeProvider.id
    access_token_url = 'https://stackexchange.com/oauth/access_token'
    authorize_url = 'https://stackexchange.com/oauth'
    profile_url = 'https://api.stackexchange.com/2.1/me'

    def complete_login(self, request, app, token, **kwargs):
        provider = registry.by_id(app.provider)
        site = provider.get_site()
        resp = requests.get(self.profile_url,
                            params={ 'access_token': token.token,
                                     'key': app.key,
                                     'site': site })
        extra_data = resp.json()['items'][0]
        # `user_id` varies if you use the same account for
        # e.g. StackOverflow and ServerFault. Therefore, we pick
        # `account_id`.
        uid = str(extra_data['account_id'])
        user = get_adapter() \
            .populate_new_user(username=extra_data.get('display_name'))
        account = SocialAccount(user=user,
                                uid=uid,
                                extra_data=extra_data,
                                provider=self.provider_id)
        return SocialLogin(account)


oauth2_login = OAuth2LoginView.adapter_view(StackExchangeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StackExchangeOAuth2Adapter)

