from django.utils.http import urlencode

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)


class TrelloOAuthAdapter(OAuthAdapter):
    provider_id = "trello"
    request_token_url = "https://trello.com/1/OAuthGetRequestToken"
    authorize_url = "https://trello.com/1/OAuthAuthorizeToken"
    access_token_url = "https://trello.com/1/OAuthGetAccessToken"

    def complete_login(self, request, app, token, response):
        # we need to get the member id and the other information
        info_url = "{base}?{query}".format(
            base="https://api.trello.com/1/members/me",
            query=urlencode({"key": app.key, "token": response.get("oauth_token")}),
        )
        resp = get_adapter().get_requests_session().get(info_url)
        resp.raise_for_status()
        extra_data = resp.json()
        result = self.get_provider().sociallogin_from_response(request, extra_data)
        return result


oauth_login = OAuthLoginView.adapter_view(TrelloOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TrelloOAuthAdapter)
