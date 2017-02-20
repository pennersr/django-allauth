import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import LineProvider


class LineOAuth2Adapter(OAuth2Adapter):
    provider_id = LineProvider.id
    access_token_url = 'https://api.line.me/v1/oauth/accessToken'
    authorize_url = 'https://access.line.me/dialog/oauth/weblogin'
    profile_url = 'https://api.line.me/v1/profile'

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(LineOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(LineOAuth2Adapter)
