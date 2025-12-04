from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class FeedlyOAuth2Adapter(OAuth2Adapter):
    provider_id = "feedly"
    host = app_settings.PROVIDERS.get(provider_id, {}).get("HOST", "cloud.feedly.com")
    access_token_url = f"https://{host}/v3/auth/token"
    authorize_url = f"https://{host}/v3/auth/auth"
    profile_url = f"https://{host}/v3/profile"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"OAuth {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FeedlyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FeedlyOAuth2Adapter)
