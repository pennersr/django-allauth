from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class GiteaOAuth2Adapter(OAuth2Adapter):
    provider_id = "gitea"
    settings = app_settings.PROVIDERS.get(provider_id, {})

    if "GITEA_URL" in settings:
        web_url = settings.get("GITEA_URL").rstrip("/")
    else:
        web_url = "https://gitea.com"
    api_url = f"{web_url}/api/v1"

    access_token_url = f"{web_url}/login/oauth/access_token"
    authorize_url = f"{web_url}/login/oauth/authorize"
    profile_url = f"{api_url}/user"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"token {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(GiteaOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GiteaOAuth2Adapter)
