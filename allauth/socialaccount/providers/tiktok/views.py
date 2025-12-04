from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.socialaccount.providers.tiktok.client import TikTokOAuth2Client
from allauth.socialaccount.providers.tiktok.scope import TikTokScope


class TikTokOAuth2Adapter(OAuth2Adapter):
    provider_id = "tiktok"
    access_token_url = "https://open.tiktokapis.com/v2/oauth/token/"  # nosec
    authorize_url = "https://www.tiktok.com/v2/auth/authorize/"
    # https://developers.tiktok.com/doc/tiktok-api-v2-get-user-info/
    profile_url = "https://open.tiktokapis.com/v2/user/info/"
    client_class = TikTokOAuth2Client
    scope_delimiter = ","

    def get_query_fields(self):
        fields = []
        if TikTokScope.user_info_basic.value in self.get_provider().get_scope():
            fields += ["open_id", "display_name", "avatar_url"]
        if TikTokScope.user_info_profile.value in self.get_provider().get_scope():
            fields += ["username", "profile_deep_link"]
        return ",".join(fields)

    def complete_login(self, request, app, token, **kwargs):
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Client-ID": app.client_id,
        }
        with get_adapter().get_requests_session() as sess:
            params = {"fields": self.get_query_fields()}
            response = sess.get(self.profile_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

        user_info = data.get("data", {}).get("user")
        return self.get_provider().sociallogin_from_response(request, user_info)


oauth2_login = OAuth2LoginView.adapter_view(TikTokOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(TikTokOAuth2Adapter)
