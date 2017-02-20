import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import EveOnlineProvider


class EveOnlineOAuth2Adapter(OAuth2Adapter):
    provider_id = EveOnlineProvider.id
    access_token_url = 'https://login.eveonline.com/oauth/token'
    authorize_url = 'https://login.eveonline.com/oauth/authorize'
    profile_url = 'https://login.eveonline.com/oauth/verify'

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(self.profile_url,
                            headers={'Authorization': 'Bearer ' + token.token})
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(EveOnlineOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(EveOnlineOAuth2Adapter)
