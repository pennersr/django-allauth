from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class DiscordOAuth2Adapter(OAuth2Adapter):
    provider_id = "discord"
    access_token_url = "https://discord.com/api/oauth2/token"  # nosec
    authorize_url = "https://discord.com/api/oauth2/authorize"
    profile_url = "https://discord.com/api/users/@me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": "Bearer {0}".format(token.token),
            "Content-Type": "application/json",
        }
        extra_data = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth2_login = OAuth2LoginView.adapter_view(DiscordOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DiscordOAuth2Adapter)
