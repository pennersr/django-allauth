import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import DigitalOceanProvider


class DigitalOceanOAuth2Adapter(OAuth2Adapter):
    provider_id = DigitalOceanProvider.id
    access_token_url = 'https://cloud.digitalocean.com/v1/oauth/token'
    authorize_url = 'https://cloud.digitalocean.com/v1/oauth/authorize'
    profile_url = 'https://api.digitalocean.com/v2/account'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DigitalOceanOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DigitalOceanOAuth2Adapter)
