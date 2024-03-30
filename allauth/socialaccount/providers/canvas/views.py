import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

# from .provider import CanvasProvider


class CanvasOAuth2Adapter(OAuth2Adapter):
    provider_id = "canvas"

    @property
    def base_url(self):
        return self.get_provider().app.key

    @property
    def access_token_url(self):
        return "{0}/login/oauth2/token/".format(self.base_url)

    @property
    def authorize_url(self):
        return "{0}/login/oauth2/auth".format(self.base_url)

    @property
    def profile_url(self):
        return "{0}/api/v1/users/self/profile".format(self.base_url)

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url, headers={"Authorization": "Bearer " + token.token}
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(CanvasOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CanvasOAuth2Adapter)
