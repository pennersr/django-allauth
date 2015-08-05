import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from .provider import BasecampProvider


class BasecampOAuth2Adapter(OAuth2Adapter):
    provider_id = BasecampProvider.id
    access_token_url = 'https://launchpad.37signals.com/authorization/token'
    authorize_url = 'https://launchpad.37signals.com/authorization/new'
    profile_url = 'https://basecamp.com/999999999/api/v1/people/me.json'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(BasecampOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(BasecampOAuth2Adapter)
