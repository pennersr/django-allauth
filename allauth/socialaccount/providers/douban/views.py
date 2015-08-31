import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import DoubanProvider


class DoubanOAuth2Adapter(OAuth2Adapter):
    provider_id = DoubanProvider.id
    access_token_url = 'https://www.douban.com/service/auth2/token'
    authorize_url = 'https://www.douban.com/service/auth2/auth'
    profile_url = 'https://api.douban.com/v2/user/~me'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer %s' % token.token}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DoubanOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DoubanOAuth2Adapter)
