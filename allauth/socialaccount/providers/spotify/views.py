from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class SpotifyOAuth2Adapter(OAuth2Adapter):
    provider_id = "spotify"
    access_token_url = "https://accounts.spotify.com/api/token"
    authorize_url = "https://accounts.spotify.com/authorize"
    profile_url = "https://api.spotify.com/v1/me"

    def complete_login(self, request, app, token, **kwargs):
        extra_data = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, params={"access_token": token.token})
        )

        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth_login = OAuth2LoginView.adapter_view(SpotifyOAuth2Adapter)
oauth_callback = OAuth2CallbackView.adapter_view(SpotifyOAuth2Adapter)
