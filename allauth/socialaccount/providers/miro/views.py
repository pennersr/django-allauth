from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class MiroOAuth2Adapter(OAuth2Adapter):
    provider_id = "miro"
    access_token_url = "https://api.miro.com/v1/oauth/token"  # nosec
    authorize_url = "https://miro.com/oauth/authorize"
    profile_url = "https://api.miro.com/v1/users/me"

    def complete_login(self, request, app, token, response):
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
        }
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(MiroOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MiroOAuth2Adapter)
