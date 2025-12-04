from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class BaiduOAuth2Adapter(OAuth2Adapter):
    provider_id = "baidu"
    access_token_url = "https://openapi.baidu.com/oauth/2.0/token"  # nosec
    authorize_url = "https://openapi.baidu.com/oauth/2.0/authorize"
    profile_url = (
        "https://openapi.baidu.com/rest/2.0/passport/users/getLoggedInUser"  # noqa
    )

    def complete_login(self, request, app, token, **kwargs):
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, params={"access_token": token.token})
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(BaiduOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BaiduOAuth2Adapter)
