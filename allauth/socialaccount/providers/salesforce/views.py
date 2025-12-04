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
        return f"{self.base_url}/services/oauth2/authorize"

    @property
    def access_token_url(self):
        return f"{self.base_url}/services/oauth2/token"

    @property
    def userinfo_url(self):
        return f"{self.base_url}/services/oauth2/userinfo"

    def complete_login(self, request, app, token, **kwargs):
        with get_adapter().get_requests_session() as sess:
            resp = sess.get(self.userinfo_url, params={"oauth_token": token.token})
            resp.raise_for_status()
            extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(SalesforceOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SalesforceOAuth2Adapter)
