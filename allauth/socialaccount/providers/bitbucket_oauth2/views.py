from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
import requests

from .provider import BitbucketOAuth2Provider


class BitbucketOAuth2Adapter(OAuth2Adapter):
    provider_id = BitbucketOAuth2Provider.id
    access_token_url = 'https://bitbucket.org/site/oauth2/access_token'
    authorize_url = 'https://bitbucket.org/site/oauth2/authorize'
    profile_url = 'https://bitbucket.org/api/1.0/user'
    redirect_uri_protocol = 'https'

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


oauth_login = OAuth2LoginView.adapter_view(BitbucketOAuth2Adapter)
oauth_callback = OAuth2CallbackView.adapter_view(BitbucketOAuth2Adapter)
