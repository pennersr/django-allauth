import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import ZohoProvider


class ZohoOAuth2Adapter(OAuth2Adapter):
    provider_id = ZohoProvider.id
    access_token_url = "https://accounts.zoho.com/oauth/v2/token"
    authorize_url = "https://accounts.zoho.com/oauth/v2/auth"
    profile_url = "https://accounts.zoho.com/oauth/user/info"

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            headers={"Authorization": "Bearer {}".format(token.token)},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(ZohoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ZohoOAuth2Adapter)
