from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)


class SalesforceOAuth2Adapter(OAuth2Adapter):
    provider_id = "salesforce"

    @property
    def base_url(self):
        return self.get_provider().app.key

    @property
    def authorize_url(self):
        return "{}/services/oauth2/authorize".format(self.base_url)

    @property
    def access_token_url(self):
        return "{}/services/oauth2/token".format(self.base_url)

    @property
    def userinfo_url(self):
        return "{}/services/oauth2/userinfo".format(self.base_url)

    def complete_login(self, request, app, token, **kwargs):
        resp = (
            get_adapter()
            .get_requests_session()
            .get(self.userinfo_url, params={"oauth_token": token})
        )
        resp.raise_for_status()
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(SalesforceOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SalesforceOAuth2Adapter)
