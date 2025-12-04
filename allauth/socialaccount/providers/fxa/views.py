from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .constants import FXA_OAUTH_ENDPOINT, FXA_PROFILE_ENDPOINT, PROVIDER_ID


class FirefoxAccountsOAuth2Adapter(OAuth2Adapter):
    provider_id = PROVIDER_ID
    access_token_url = f"{FXA_OAUTH_ENDPOINT}/token"
    authorize_url = f"{FXA_OAUTH_ENDPOINT}/authorization"
    profile_url = f"{FXA_PROFILE_ENDPOINT}/profile"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.profile_url, headers=headers)
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FirefoxAccountsOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FirefoxAccountsOAuth2Adapter)
