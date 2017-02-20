import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import CoinbaseProvider


class CoinbaseOAuth2Adapter(OAuth2Adapter):
    provider_id = CoinbaseProvider.id

    @property
    def authorize_url(self):
        return 'https://coinbase.com/oauth/authorize'

    @property
    def access_token_url(self):
        return 'https://coinbase.com/oauth/token'

    @property
    def profile_url(self):
        return 'https://coinbase.com/api/v1/users'

    def complete_login(self, request, app, token, **kwargs):
        response = requests.get(self.profile_url,
                                params={'access_token': token})
        extra_data = response.json()['users'][0]['user']
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(CoinbaseOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CoinbaseOAuth2Adapter)
