import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import HubSpotProvider


class HubSpotOAuth2Adapter(OAuth2Adapter):
    provider_id = HubSpotProvider.id
    access_token_url = 'https://api.hubapi.com/oauth/v1/token'
    authorize_url = 'https://app.hubspot.com/oauth/authorize'
    token_metadata = 'https://api.hubapi.com/oauth/v1/access-tokens/'
    redirect_uri_protocol = 'https'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.token_metadata + token.token)
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(HubSpotOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(HubSpotOAuth2Adapter)
