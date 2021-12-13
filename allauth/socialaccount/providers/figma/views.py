import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import FigmaProvider


class FigmaOAuth2Adapter(OAuth2Adapter):
    provider_id = FigmaProvider.id

    authorize_url = "https://www.figma.com/oauth"
    access_token_url = "https://www.figma.com/api/oauth/token"
    userinfo_url = "https://api.figma.com/v1/me"

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.userinfo_url,
            headers={"Authorization": "Bearer {0}".format(token.token)},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FigmaOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FigmaOAuth2Adapter)
