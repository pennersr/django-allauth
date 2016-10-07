import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import DoximityProvider


class DoximityOAuth2Adapter(OAuth2Adapter):
    provider_id = DoximityProvider.id
    access_token_url = 'https://auth.doximity.com/oauth/token'
    authorize_url = 'https://auth.doximity.com/oauth/authorize'
    profile_url = 'https://www.doximity.com/api/v1/users/current'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer %s' % token.token}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DoximityOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DoximityOAuth2Adapter)
