from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class JupyterHubOAuth2Adapter(OAuth2Adapter):
    provider_id = "jupyterhub"

    settings = app_settings.PROVIDERS.get(provider_id, {})
    provider_base_url = settings.get("API_URL", "")

    access_token_url = f"{provider_base_url}/hub/api/oauth2/token"
    authorize_url = f"{provider_base_url}/hub/api/oauth2/authorize"
    profile_url = f"{provider_base_url}/hub/api/user"

    def complete_login(self, request, app, token: SocialToken, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            user_profile = resp.json()

        return self.get_provider().sociallogin_from_response(request, user_profile)


oauth2_login = OAuth2LoginView.adapter_view(JupyterHubOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(JupyterHubOAuth2Adapter)
