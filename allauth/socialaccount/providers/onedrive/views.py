import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import OnedriveOAuth2Provider


class OnedriveOAuth2Adapter(OAuth2Adapter):
    provider_id = OnedriveOAuth2Provider.id
    access_token_url = 'https://login.live.com/oauth20_token.srf'
    authorize_url = 'https://login.live.com/oauth20_authorize.srf'
    profile_url = 'https://apis.live.net/v5.0/me'
    redirect_uri_protocol = None

    def complete_login(self, request, app, token, **kwargs):
        extra_data = requests.get(self.profile_url, params={
            'access_token': token.token
        })

        # This only here because of weird response from the test suite
        if isinstance(extra_data, list):
            extra_data = extra_data[0]

        return self.get_provider().sociallogin_from_response(
            request,
            extra_data.json()
        )


oauth_login = OAuth2LoginView.adapter_view(OnedriveOAuth2Adapter)
oauth_callback = OAuth2CallbackView.adapter_view(OnedriveOAuth2Adapter)
