from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class FigmaOAuth2Adapter(OAuth2Adapter):
    provider_id = "figma"

    authorize_url = "https://www.figma.com/oauth"
    access_token_url = "https://www.figma.com/api/oauth/token"  # nosec
    userinfo_url = "https://api.figma.com/v1/me"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.userinfo_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FigmaOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FigmaOAuth2Adapter)
