from ..oauth.views import OAuthAdapter, OAuthCallbackView, OAuthLoginView
from .client import PocketOAuthClient
from .provider import PocketProvider


class PocketOAuthAdapter(OAuthAdapter):
    provider_id = PocketProvider.id
    request_token_url = "https://getpocket.com/v3/oauth/request"
    access_token_url = "https://getpocket.com/v3/oauth/authorize"
    authorize_url = "https://getpocket.com/auth/authorize"

    def complete_login(self, request, app, token, response):
        return self.get_provider().sociallogin_from_response(request, response)


class PocketOAuthLoginView(OAuthLoginView):
    def _get_client(self, request, callback_url):
        provider = self.adapter.get_provider()
        app = provider.get_app(request)
        scope = " ".join(provider.get_scope(request))
        parameters = {}
        if scope:
            parameters["scope"] = scope
        client = PocketOAuthClient(
            request,
            app.client_id,
            app.secret,
            self.adapter.request_token_url,
            self.adapter.access_token_url,
            callback_url,
            parameters=parameters,
            provider=provider,
        )
        return client


class PocketOAuthCallbackView(OAuthCallbackView):
    def _get_client(self, request, callback_url):
        provider = self.adapter.get_provider()
        app = provider.get_app(request)
        scope = " ".join(provider.get_scope(request))
        parameters = {}
        if scope:
            parameters["scope"] = scope
        client = PocketOAuthClient(
            request,
            app.client_id,
            app.secret,
            self.adapter.request_token_url,
            self.adapter.access_token_url,
            callback_url,
            parameters=parameters,
            provider=provider,
        )
        return client


oauth_login = PocketOAuthLoginView.adapter_view(PocketOAuthAdapter)
oauth_callback = PocketOAuthCallbackView.adapter_view(PocketOAuthAdapter)
