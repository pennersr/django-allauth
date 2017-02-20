import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import AsanaProvider


class AsanaOAuth2Adapter(OAuth2Adapter):
    provider_id = AsanaProvider.id
    access_token_url = 'https://app.asana.com/-/oauth_token'
    authorize_url = 'https://app.asana.com/-/oauth_authorize'
    profile_url = 'https://app.asana.com/api/1.0/users/me'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()['data']
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(AsanaOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(AsanaOAuth2Adapter)
