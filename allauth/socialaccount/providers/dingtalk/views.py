import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .client import DingTalkOAuth2Client
from .provider import DingTalkProvider


class DingTalkOAuth2Adapter(OAuth2Adapter):
    provider_id = DingTalkProvider.id
    access_token_url = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
    authorize_url = "https://login.dingtalk.com/oauth2/auth"
    profile_url = "https://api.dingtalk.com/v1.0/contact/users/me"
    client_class = DingTalkOAuth2Client

    def __init__(self, request):
        # dingtalk set "authCode" instead of "code" in callback url
        if "authCode" in request.GET:
            request.GET._mutable = True
            request.GET["code"] = request.GET["authCode"]
            request.GET._mutable = False

        super(DingTalkOAuth2Adapter, self).__init__(request)

    def complete_login(self, request, app, token, **kwargs):
        headers = {"x-acs-dingtalk-access-token": token.token}
        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DingTalkOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DingTalkOAuth2Adapter)
