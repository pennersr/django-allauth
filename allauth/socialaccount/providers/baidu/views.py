import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import BaiduProvider


class BaiduOAuth2Adapter(OAuth2Adapter):
    provider_id = BaiduProvider.id
    access_token_url = "https://openapi.baidu.com/oauth/2.0/token"
    authorize_url = "https://openapi.baidu.com/oauth/2.0/authorize"
    profile_url = (
        "https://openapi.baidu.com/rest/2.0/passport/users/getLoggedInUser"  # noqa
    )

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url, params={"access_token": token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(BaiduOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BaiduOAuth2Adapter)
