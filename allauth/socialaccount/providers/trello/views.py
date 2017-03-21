import requests

from allauth.socialaccount.providers.oauth.views import (
    OAuthAdapter,
    OAuthCallbackView,
    OAuthLoginView,
)

from .provider import TrelloProvider


class TrelloOAuthAdapter(OAuthAdapter):
    provider_id = TrelloProvider.id
    request_token_url = 'https://trello.com/1/OAuthGetRequestToken'
    authorize_url = 'https://trello.com/1/OAuthAuthorizeToken'
    access_token_url = 'https://trello.com/1/OAuthGetAccessToken'


    def complete_login(self, request, app, token, response):
        # we need to get the member id and the other information
        # check: https://developers.trello.com/advanced-reference/token
        # https://api.trello.com/1/tokens/91a6408305c1e5ec1b0b306688bc2e2f8fe67abf6a2ecec38c17e5b894fcf866?key=[application_key]&token=[optional_auth_token]
        baseURL = 'https://api.trello.com/1/tokens/'
        infoURL = baseURL + '{token}?key={app_key}&token={oauth_token}'.format(
            token=token,
            app_key=app.key,
            oauth_token=response.get('oauth_token')
            )
        reqResp = requests.get(infoURL)
        extra_data = reqResp.json()
        result = self.get_provider().sociallogin_from_response(request,
                                                               extra_data)
        return result


oauth_login = OAuthLoginView.adapter_view(TrelloOAuthAdapter)
oauth_callback = OAuthCallbackView.adapter_view(TrelloOAuthAdapter)
