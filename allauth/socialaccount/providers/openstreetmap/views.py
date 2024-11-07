from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


class OpenStreetMapAPI(OAuth):
    url = "https://api.openstreetmap.org/api/0.6/user/details.json"

    def get_user_info(self):
        data = self.query(self.url).json()
        return data["user"]


class OpenStreetMapOAuthAdapter(OAuthAdapter):
    provider_id = "openstreetmap"
    request_token_url = "https://www.openstreetmap.org/oauth/request_token"  # nosec
    access_token_url = "https://www.openstreetmap.org/oauth/access_token"  # nosec
    authorize_url = "https://www.openstreetmap.org/oauth/authorize"

    def complete_login(self, request, app, token, response):
        client = OpenStreetMapAPI(
            request, app.client_id, app.secret, self.request_token_url
        )
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(OpenStreetMapOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(OpenStreetMapOAuthAdapter)
