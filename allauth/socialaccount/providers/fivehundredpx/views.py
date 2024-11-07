from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


API_BASE = "https://api.500px.com/v1"


class FiveHundredPxAPI(OAuth):
    """
    Verifying 500px credentials
    """

    url = API_BASE + "/users"

    def get_user_info(self):
        return self.query(self.url).json()["user"]


class FiveHundredPxOAuthAdapter(OAuthAdapter):
    provider_id = "500px"
    request_token_url = API_BASE + "/oauth/request_token"
    access_token_url = API_BASE + "/oauth/access_token"
    authorize_url = API_BASE + "/oauth/authorize"

    def complete_login(self, request, app, token, response):
        client = FiveHundredPxAPI(
            request, app.client_id, app.secret, self.request_token_url
        )
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(FiveHundredPxOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(FiveHundredPxOAuthAdapter)
