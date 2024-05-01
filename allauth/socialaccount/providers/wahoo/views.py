from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class WahooOAuth2Adapter(OAuth2Adapter):
    provider_id = "wahoo"
    access_token_url = "https://api.wahooligan.com/oauth/token"
    authorize_url = "https://api.wahooligan.com/oauth/authorize"
    profile_url = "https://api.wahooligan.com/v1/user"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(WahooOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(WahooOAuth2Adapter)
