from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class SoundCloudOAuth2Adapter(OAuth2Adapter):
    provider_id = "soundcloud"
    access_token_url = "https://api.soundcloud.com/oauth2/token"  # nosec
    authorize_url = "https://soundcloud.com/connect"
    profile_url = "https://api.soundcloud.com/me.json"

    def complete_login(self, request, app, token, **kwargs):
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, params={"oauth_token": token.token})
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(SoundCloudOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SoundCloudOAuth2Adapter)
