import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import WhaleSpaceProvider


class WhaleSpaceOAuth2Adapter(OAuth2Adapter):
    provider_id = WhaleSpaceProvider.id
    access_token_url = "https://auth.whalespace.io/oauth2/v1/token"
    authorize_url = "https://auth.whalespace.io/oauth2/v1/authorize"
    profile_url = "https://auth.whalespace.io/oauth2/v1/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        resp.raise_for_status()
        extra_data = resp.json().get("response")
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(WhaleSpaceOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WhaleSpaceOAuth2Adapter)
