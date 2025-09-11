from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


class DiscogsAPI(OAuth):
    url = "https://api.discogs.com/oauth/identity"

    def get_user_info(self):
        data = self.query(self.url).json()
        return data


class DiscogsOAuthAdapter(OAuthAdapter):
    provider_id = "discogs"
    request_token_url = "https://api.discogs.com/oauth/request_token"  # nosec
    access_token_url = "https://api.discogs.com/oauth/access_token"  # nosec
    authorize_url = "https://discogs.com/oauth/authorize"

    def complete_login(self, request, app, token, response):
        client = DiscogsAPI(request, app.client_id, app.secret, self.request_token_url)
        extra_data = client.get_user_info()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth_login = OAuthLoginView.adapter_view(DiscogsOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(DiscogsOAuthAdapter)
