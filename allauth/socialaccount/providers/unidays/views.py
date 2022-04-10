import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import UNiDAYSProvider


class UNiDAYSOAuth2Adapter(OAuth2Adapter):
    provider_id = UNiDAYSProvider.id
    access_token_url = "https://account.myunidays.com/oauth/token"
    authorize_url = "https://account.myunidays.com/oauth/authorize"
    profile_url = "https://account.myunidays.com/oauth/userinfo "

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            headers={"Authorization": f"Bearer: {token.token}"},
        )

        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(UNiDAYSOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(UNiDAYSOAuth2Adapter)
