from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class FrontierOAuth2Adapter(OAuth2Adapter):
    provider_id = "frontier"
    AUTH_API = "https://auth.frontierstore.net"
    access_token_url = f"{AUTH_API}/token"
    authorize_url = f"{AUTH_API}/auth"
    profile_url = f"{AUTH_API}/me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FrontierOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FrontierOAuth2Adapter)
