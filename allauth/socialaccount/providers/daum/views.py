import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import DaumProvider


class DaumOAuth2Adapter(OAuth2Adapter):
    provider_id = DaumProvider.id
    access_token_url = "https://apis.daum.net/oauth2/token"
    authorize_url = "https://apis.daum.net/oauth2/authorize"
    profile_url = "https://apis.daum.net/user/v1/show.json"

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url, params={"access_token": token.token})
        extra_data = resp.json().get("result")
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(DaumOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DaumOAuth2Adapter)
