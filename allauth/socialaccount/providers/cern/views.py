import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import CernProvider


class CernOAuth2Adapter(OAuth2Adapter):
    provider_id = CernProvider.id
    access_token_url = "https://oauth.web.cern.ch/OAuth/Token"
    authorize_url = "https://oauth.web.cern.ch/OAuth/Authorize"
    profile_url = "https://oauthresource.web.cern.ch/api/User"
    groups_url = "https://oauthresource.web.cern.ch/api/Groups"

    supports_state = False
    redirect_uri_protocol = "https"

    def complete_login(self, request, app, token, **kwargs):
        headers = {"Authorization": "Bearer {0}".format(token.token)}
        user_response = requests.get(self.profile_url, headers=headers)
        groups_response = requests.get(self.groups_url, headers=headers)
        extra_data = user_response.json()
        extra_data.update(groups_response.json())
        return self.get_provider().sociallogin_from_response(request, extra_data)


oauth2_login = OAuth2LoginView.adapter_view(CernOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(CernOAuth2Adapter)
