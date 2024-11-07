from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class CILogonOAuth2Adapter(OAuth2Adapter):
    provider_id = "cilogon"
    access_token_url = "https://cilogon.org/oauth2/token"  # nosec
    authorize_url = "https://cilogon.org/authorize"
    profile_url = "https://cilogon.org/oauth2/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                params={"access_token": token.token, "alt": "json"},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(CILogonOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CILogonOAuth2Adapter)
