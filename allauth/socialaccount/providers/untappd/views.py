from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .client import UntappdOAuth2Client
from .provider import UntappdProvider


class UntappdOAuth2Adapter(OAuth2Adapter):
    client_class = UntappdOAuth2Client
    provider_id = UntappdProvider.id
    access_token_url = "https://untappd.com/oauth/authorize/"
    access_token_method = "GET"
    authorize_url = "https://untappd.com/oauth/authenticate/"
    user_info_url = "https://api.untappd.com/v4/user/info/"
    supports_state = False

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.user_info_url, params={"access_token": token.token})
        )
        extra_data = resp.json()
        # TODO: get and store the email from the user info json
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(UntappdOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(UntappdOAuth2Adapter)
