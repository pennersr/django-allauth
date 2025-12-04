from allauth.core import context
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class NextCloudOAuth2Adapter(OAuth2Adapter):
    provider_id = "nextcloud"

    def _build_server_url(self, path):
        settings = app_settings.PROVIDERS.get(self.provider_id, {})
        server = settings.get("SERVER", "https://nextcloud.example.org")
        # Prefer app based setting.
        app = get_adapter().get_app(context.request, provider=self.provider_id)
        server = app.settings.get("server", server)
        ret = f"{server}{path}"
        return ret

    @property
    def access_token_url(self):
        return self._build_server_url("/apps/oauth2/api/v1/token")

    @property
    def authorize_url(self):
        return self._build_server_url("/apps/oauth2/authorize")

    @property
    def profile_url(self):
        return self._build_server_url("/ocs/v1.php/cloud/users/")

    def complete_login(self, request, app, token: SocialToken, **kwargs):
        extra_data = self.get_user_info(token, kwargs["response"]["user_id"])
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_user_info(self, token: SocialToken, user_id):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(
                f"{self.profile_url}{user_id}",
                params={"format": "json"},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()["ocs"]["data"]
        return data


oauth2_login = OAuth2LoginView.adapter_view(NextCloudOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(NextCloudOAuth2Adapter)
