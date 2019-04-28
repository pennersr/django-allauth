import requests

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import SlackProvider


class SlackOAuth2Adapter(OAuth2Adapter):
    provider_id = SlackProvider.id

    access_token_url = 'https://slack.com/api/oauth.access'
    authorize_url = 'https://slack.com/oauth/authorize'
    identity_url = 'https://slack.com/api/users.identity'

    def complete_login(self, request, app, token, **kwargs):
        extra_data = self.get_data(token.token)
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)

    def get_data(self, token):
        # Verify the user first
        resp = requests.get(
            self.identity_url,
            params={'token': token}
        )
        resp = resp.json()

        if not resp.get('ok'):
            raise OAuth2Error()

        return resp


oauth2_login = OAuth2LoginView.adapter_view(SlackOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SlackOAuth2Adapter)
