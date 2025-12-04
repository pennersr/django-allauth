from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class ZoomOAuth2Adapter(OAuth2Adapter):
    provider_id = "zoom"
    access_token_url = "https://zoom.us/oauth/token"  # nosec
    authorize_url = "https://zoom.us/oauth/authorize"
    profile_url = "https://api.zoom.us/v2/users/me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(ZoomOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ZoomOAuth2Adapter)
