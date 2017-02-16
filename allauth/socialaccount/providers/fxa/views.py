import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import (
    FXA_OAUTH_ENDPOINT,
    FXA_PROFILE_ENDPOINT,
    FirefoxAccountsProvider,
)


class FirefoxAccountsOAuth2Adapter(OAuth2Adapter):
    provider_id = FirefoxAccountsProvider.id
    access_token_url = FXA_OAUTH_ENDPOINT + '/token'
    authorize_url = FXA_OAUTH_ENDPOINT + '/authorization'
    profile_url = FXA_PROFILE_ENDPOINT + '/profile'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FirefoxAccountsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FirefoxAccountsOAuth2Adapter)
