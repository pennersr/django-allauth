from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import YNABProvider


class YNABOAuth2Adapter(OAuth2Adapter):
    provider_id = YNABProvider.id
    access_token_url = "https://app.youneedabudget.com/oauth/token"
    authorize_url = "https://app.youneedabudget.com/oauth/authorize"
    profile_url = "https://api.youneedabudget.com/v1/user"

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                headers={"Authorization": "Bearer {}".format(token.token)},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(YNABOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(YNABOAuth2Adapter)
