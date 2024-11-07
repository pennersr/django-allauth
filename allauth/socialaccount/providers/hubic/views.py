from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class HubicOAuth2Adapter(OAuth2Adapter):
    provider_id = "hubic"
    access_token_url = "https://api.hubic.com/oauth/token"  # nosec
    authorize_url = "https://api.hubic.com/oauth/auth"
    profile_url = "https://api.hubic.com/1.0/account"
    redirect_uri_protocol = "https"

    def complete_login(self, request, app, token, **kwargs):
        token_type = kwargs["response"]["token_type"]
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers={"Authorization": "%s %s" % (token_type, token.token)},
            )
        )
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(HubicOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(HubicOAuth2Adapter)
