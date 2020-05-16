import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import MixerProvider


class MixerOAuth2Adapter(OAuth2Adapter):
    provider_id = MixerProvider.id
    access_token_url = 'https://mixer.com/api/v1/oauth/token'
    authorize_url = 'https://mixer.com/oauth/authorize'
    profile_url = 'https://mixer.com/api/v1/users/current'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {}'.format(token.token)}
        response = requests.get(self.profile_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        return self.get_provider().sociallogin_from_response(
            request, data
        )


oauth2_login = OAuth2LoginView.adapter_view(MixerOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MixerOAuth2Adapter)
