import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import FirefoxAccountsProvider


class FirefoxAccountsOAuth2Adapter(OAuth2Adapter):
    provider_id = FirefoxAccountsProvider.id
    access_token_url = 'https://oauth.accounts.firefox.com/v1/token'
    authorize_url = 'https://oauth.accounts.firefox.com/v1/authorization'
    profile_url = 'https://profile.accounts.firefox.com/v1/profile'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FirefoxAccountsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FirefoxAccountsOAuth2Adapter)
