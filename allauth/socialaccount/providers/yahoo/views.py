from __future__ import unicode_literals

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import YahooProvider


class YahooOAuth2Adapter(OAuth2Adapter):
    provider_id = YahooProvider.id
    access_token_url = "https://api.login.yahoo.com/oauth2/get_token"
    authorize_url = "https://api.login.yahoo.com/oauth2/request_auth"
    profile_url = "https://api.login.yahoo.com/openid/v1/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = (
            get_adapter().get_requests_session().get(self.profile_url, headers=headers)
        )
        resp.raise_for_status()

        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(YahooOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(YahooOAuth2Adapter)
