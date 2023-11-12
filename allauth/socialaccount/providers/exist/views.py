import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import ExistProvider


class ExistOAuth2Adapter(OAuth2Adapter):
    provider_id = ExistProvider.id
    access_token_url = "https://exist.io/oauth2/access_token"
    authorize_url = "https://exist.io/oauth2/authorize"
    profile_url = "https://exist.io/api/2/accounts/profile/"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(ExistOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(ExistOAuth2Adapter)
