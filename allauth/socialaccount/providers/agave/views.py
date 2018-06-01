import requests

from allauth.socialaccount.providers.agave.provider import AgaveProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class AgaveAdapter(OAuth2Adapter):
    provider_id = AgaveProvider.id
    provider_default_url = 'https://public.agaveapi.co/'
    provider_api_version = 'v2'

    provider_base_url = 'https://public.agaveapi.co'

    access_token_url = '{0}/token'.format(provider_base_url)
    authorize_url = '{0}/authorize'.format(provider_base_url)
    profile_url = '{0}/profiles/v2/me'.format(provider_base_url)

    def complete_login(self, request, app, token, response):
        extra_data = requests.get(self.profile_url, params={
            'access_token': token.token
        }, headers={
            'Authorization': 'Bearer ' + token.token,
        })

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data.json()['result']
        )


oauth2_login = OAuth2LoginView.adapter_view(AgaveAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AgaveAdapter)
