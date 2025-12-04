from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class GlobusOAuth2Adapter(OAuth2Adapter):
    provider_id = "globus"
    provider_default_url = "https://auth.globus.org/v2/oauth2"

    provider_base_url = "https://auth.globus.org/v2/oauth2"

    access_token_url = f"{provider_base_url}/token"
    authorize_url = f"{provider_base_url}/authorize"
    profile_url = f"{provider_base_url}/userinfo"

    def complete_login(self, request, app, token, response):
        headers = {"Authorization": f"Bearer {token.token}"}
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(
                self.profile_url,
                params={"access_token": token.token},
                headers=headers,
            )
            extra_data = resp.json()

        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(GlobusOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GlobusOAuth2Adapter)
