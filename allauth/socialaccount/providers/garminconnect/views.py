import json

from allauth.socialaccount.providers.oauth.client import OAuth
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)

from .client import GarminConnectOAuthClient
from .provider import GarminConnectProvider


class GarminConnectAPI(OAuth):
    url = "https://apis.garmin.com/wellness-api/rest/user/id"

    def get_user_info(self):
        data = json.loads(self.query(self.url))
        return data


class GarminConnectOAuthAdapter(OAuthAdapter):
    provider_id = GarminConnectProvider.id
    request_token_url = (
        "https://connectapi.garmin.com/oauth-service/oauth/request_token"
    )
    access_token_url = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    authorize_url = "https://connect.garmin.com/oauthConfirm"

    def complete_login(self, request, app, token, response):
        client = GarminConnectAPI(
            request, app.client_id, app.secret, self.request_token_url
        )
        extra_data = client.get_user_info()

        return self.get_provider().sociallogin_from_response(request, extra_data)


class GetClientMixin(object):
    """
    Mixin handling common code for OAuthLoginView and OAuthCallbackView
    """
    def _get_client(self, request, callback_url):
        provider = self.adapter.get_provider()
        app = provider.app
        scope = " ".join(provider.get_scope(request))
        parameters = {}
        if scope:
            parameters["scope"] = scope
        client = GarminConnectOAuthClient(
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


class GarminConnectLoginView(GetClientMixin, OAuthLoginView):
    pass


class GarminConnectOAuthCallbackView(GetClientMixin, OAuthCallbackView):
    pass


oauth_login = GarminConnectLoginView.adapter_view(GarminConnectOAuthAdapter)
oauth_callback = GarminConnectOAuthCallbackView.adapter_view(GarminConnectOAuthAdapter)
