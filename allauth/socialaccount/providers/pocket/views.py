from ..oauth.views import OAuthAdapter, OAuthCallbackView, OAuthLoginView
from .client import PocketOAuthClient


class PocketOAuthAdapter(OAuthAdapter):
    provider_id = "pocket"
    request_token_url = "https://getpocket.com/v3/oauth/request"  # nosec
    access_token_url = "https://getpocket.com/v3/oauth/authorize"  # nosec
    authorize_url = "https://getpocket.com/auth/authorize"
    client_class = PocketOAuthClient

    def complete_login(self, request, app, token, response):
        return self.get_provider().sociallogin_from_response(request, response)


oauth_login = OAuthLoginView.adapter_view(PocketOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(PocketOAuthAdapter)
