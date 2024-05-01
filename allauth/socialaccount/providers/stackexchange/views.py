from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class StackExchangeOAuth2Adapter(OAuth2Adapter):
    provider_id = "stackexchange"
    access_token_url = "https://stackexchange.com/oauth/access_token"
    authorize_url = "https://stackexchange.com/oauth"
    profile_url = "https://api.stackexchange.com/2.1/me"

    def complete_login(self, request, app, token, **kwargs):
        provider = self.get_provider()
        site = provider.get_site()
        resp = (
            get_adapter()
            .get_requests_session()
            .get(
                self.profile_url,
                params={"access_token": token.token, "key": app.key, "site": site},
            )
        )
        resp.raise_for_status()
        extra_data = resp.json()["items"][0]
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(StackExchangeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StackExchangeOAuth2Adapter)
