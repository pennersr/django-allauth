import requests

from allauth.socialaccount.providers.miro.provider import MiroProvider
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class MiroOAuth2Adapter(OAuth2Adapter):
    provider_id = MiroProvider.id
    access_token_url = "https://api.miro.com/v1/oauth/token"
    authorize_url = "https://miro.com/oauth/authorize"
    profile_url = "https://api.miro.com/v1/users/me"

    def complete_login(self, request, app, token, response):
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json",
        }
        extra_data = requests.get(self.profile_url, headers=headers)
        extra_data.raise_for_status()
        return self.get_provider().sociallogin_from_response(request, extra_data.json())


oauth2_login = OAuth2LoginView.adapter_view(MiroOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MiroOAuth2Adapter)
