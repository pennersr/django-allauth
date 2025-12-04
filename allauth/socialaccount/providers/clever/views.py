from http import HTTPStatus

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class CleverOAuth2Adapter(OAuth2Adapter):
    provider_id = "clever"

    access_token_url = "https://clever.com/oauth/tokens"  # nosec
    authorize_url = "https://clever.com/oauth/authorize"
    identity_url = "https://api.clever.com/v3.0/me"
    user_details_url = "https://api.clever.com/v3.0/users"

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request, extra_data)

    def get_data(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        with get_adapter().get_requests_session() as sess:
            # Verify the user first
            resp = sess.get(self.identity_url, headers=headers)
            if resp.status_code != HTTPStatus.OK:
                raise OAuth2Error()
            resp = resp.json()
            user_id = resp["data"]["id"]
            details_url = f"{self.user_details_url}/{user_id}"
            resp = sess.get(details_url, headers=headers)
            resp.raise_for_status()
            return resp.json()


oauth2_login = OAuth2LoginView.adapter_view(CleverOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CleverOAuth2Adapter)
