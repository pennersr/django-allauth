import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import TwitchProvider


class TwitchOAuth2Adapter(OAuth2Adapter):
    provider_id = TwitchProvider.id
    access_token_url = 'https://api.twitch.tv/kraken/oauth2/token'
    authorize_url = 'https://api.twitch.tv/kraken/oauth2/authorize'
    profile_url = 'https://api.twitch.tv/kraken/user'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={'oauth_token': token.token,
                    'client_id': app.client_id})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(TwitchOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TwitchOAuth2Adapter)
