from datetime import timedelta

from django.utils import timezone

from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class LineOAuth2Adapter(OAuth2Adapter):
    provider_id = "line"
    access_token_url = "https://api.line.me/oauth2/v2.1/token"  # nosec
    authorize_url = "https://access.line.me/oauth2/v2.1/authorize"
    profile_url = "https://api.line.me/v2/profile"  # https://developers.line.biz/en/reference/line-login/#get-user-profile
    # https://developers.line.biz/en/reference/line-login/#verify-id-token
    id_token_url = "https://api.line.me/oauth2/v2.1/verify"  # nosec

    def parse_token(self, data):
        """
        data: access_token data from line
        """
        settings = app_settings.PROVIDERS.get(self.provider_id, {})
        if "email" in settings.get("SCOPE", ""):
            token = SocialToken(token=data["id_token"])
        else:
            token = SocialToken(token=data["access_token"])
        token.token_secret = data.get("refresh_token", "")
        expires_in = data.get(self.expires_in_key, None)
        if expires_in:
            token.expires_at = timezone.now() + timedelta(seconds=int(expires_in))

        return token

    def complete_login(self, request, app, token, **kwargs):
        settings = app_settings.PROVIDERS.get(self.provider_id, {})
        with get_adapter().get_requests_session() as sess:
            if "email" in settings.get("SCOPE", ""):
                payload = {"client_id": app.client_id, "id_token": token.token}
                resp = sess.post(self.id_token_url, payload)
            else:
                headers = {"Authorization": f"Bearer {token.token}"}
                resp = sess.get(self.profile_url, headers=headers)
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(LineOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LineOAuth2Adapter)
