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
    access_token_url = 'https://id.twitch.tv/oauth2/token'
    authorize_url = 'https://id.twitch.tv/oauth2/authorize'
    profile_url = 'https://api.twitch.tv/helix/users'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {}'.format(token.token)}
        response = requests.get(self.profile_url, headers=headers)

        data = response.json()
        if response.status_code >= 400:
            error = data.get("error", "")
            message = data.get("message", "")
            raise OAuth2Error("Twitch API Error: %s (%s)" % (error, message))

        try:
            user_info = data.get('data', [])[0]
        except IndexError:
            raise OAuth2Error("Invalid data from Twitch API: %s" % (data))

        if "id" not in user_info:
            raise OAuth2Error("Invalid data from Twitch API: %s" % (user_info))

        return self.get_provider().sociallogin_from_response(
            request, user_info
        )


oauth2_login = OAuth2LoginView.adapter_view(TwitchOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TwitchOAuth2Adapter)
