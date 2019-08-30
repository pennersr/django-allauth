import requests

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
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
        params = {"oauth_token": token.token, "client_id": app.client_id}
        response = requests.get(self.profile_url, params=params)

        data = response.json()
        if response.status_code >= 400:
            error = data.get("error", "")
            message = data.get("message", "")
            raise OAuth2Error("Twitch API Error: %s (%s)" % (error, message))

        if "_id" not in data:
            raise OAuth2Error("Invalid data from Twitch API: %r" % (data))

        return self.get_provider().sociallogin_from_response(request, data)


oauth2_login = OAuth2LoginView.adapter_view(TwitchOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TwitchOAuth2Adapter)
