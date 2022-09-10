import requests

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import CleverProvider


class CleverOAuth2Adapter(OAuth2Adapter):
    provider_id = CleverProvider.id

    access_token_url = "https://clever.com/oauth/tokens"
    authorize_url = "https://clever.com/oauth/authorize"
    identity_url = "https://api.clever.com/v3.0/me"
    user_details_url = "https://api.clever.com/v3.0/users"

    supports_state = True

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_data(self, token):
        # Verify the user first
        resp = requests.get(
            self.identity_url, headers={"Authorization": "Bearer {}".format(token)}
        )
        if resp.status_code != 200:
            raise OAuth2Error()
        resp = resp.json()
        user_id = resp.get("data", {}).get("id")
        user_details = requests.get(
            "{}/{}".format(self.user_details_url, user_id),
            headers={"Authorization": "Bearer {}".format(token)},
        )
        user_details.raise_for_status()
        user_details = user_details.json()
        return user_details


oauth2_login = OAuth2LoginView.adapter_view(CleverOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CleverOAuth2Adapter)
