"""
Views for PatreonProvider
https://www.patreon.com/platform/documentation/oauth
"""

import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import PatreonProvider


class PatreonOAuth2Adapter(OAuth2Adapter):
    provider_id = PatreonProvider.id
    access_token_url = 'https://www.patreon.com/api/oauth2/token'
    authorize_url = 'https://www.patreon.com/oauth2/authorize'
    profile_url = 'https://www.patreon.com/api/oauth2/api/current_user'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            headers={'Authorization': 'Bearer ' + token.token})
        extra_data = resp.json().get('data')
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(PatreonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(PatreonOAuth2Adapter)
