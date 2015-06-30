import requests

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)

from .provider import FakeProvider


class FakeOAuth2Adapter(OAuth2Adapter):
    provider_id = FakeProvider.id
    access_token_url = 'https://localhost/o/oauth2/token'
    authorize_url = 'https://localhost/o/oauth2/auth'
    profile_url = 'https://localhost/oauth2/v1/userinfo'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            params={'access_token': token.token,
                                    'alt': 'json'})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(
            request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(FakeOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(FakeOAuth2Adapter)
