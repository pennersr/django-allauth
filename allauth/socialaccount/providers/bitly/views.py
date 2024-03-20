from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class BitlyOAuth2Adapter(OAuth2Adapter):
    provider_id = "bitly"
    access_token_url = "https://api-ssl.bitly.com/oauth/access_token"
    authorize_url = "https://bitly.com/oauth/authorize"
    profile_url = "https://api-ssl.bitly.com/v3/user/info"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.profile_url, params={"access_token": token.token})
        )
        extra_data = resp.json()["data"]
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(BitlyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BitlyOAuth2Adapter)
