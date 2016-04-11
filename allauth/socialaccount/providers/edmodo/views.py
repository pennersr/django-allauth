import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import EdmodoProvider


class EdmodoOAuth2Adapter(OAuth2Adapter):
    provider_id = EdmodoProvider.id
    access_token_url = 'https://api.edmodo.com/oauth/token'
    authorize_url = 'https://api.edmodo.com/oauth/authorize'
    profile_url = 'https://api.edmodo.com/users/me'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(EdmodoOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EdmodoOAuth2Adapter)
