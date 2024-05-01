from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .client import WeixinOAuth2Client


class WeixinOAuth2Adapter(OAuth2Adapter):
    provider_id = "weixin"
    access_token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
    profile_url = "https://api.weixin.qq.com/sns/userinfo"
    client_class = WeixinOAuth2Client

    @property
    def authorize_url(self):
        settings = self.get_provider().get_settings()
        url = settings.get(
            "AUTHORIZE_URL", "https://open.weixin.qq.com/connect/qrconnect"
        )
        return url

    def complete_login(self, request, app, token, **kwargs):
        openid = kwargs.get("response", {}).get("openid")
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                params={"access_token": token.token, "openid": openid},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()
        nickname = extra_data.get("nickname")
        if nickname:
            extra_data["nickname"] = nickname.encode("raw_unicode_escape").decode(
                "utf-8"
            )
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(WeixinOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WeixinOAuth2Adapter)
