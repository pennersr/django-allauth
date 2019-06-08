import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import StravaProvider


class StravaOauth2Adapter(OAuth2Adapter):
    provider_id = StravaProvider.id
    access_token_url = "https://www.strava.com/oauth/token"
    authorize_url = "https://www.strava.com/oauth/authorize"
    profile_url = "https://www.strava.com/api/v3/athlete"

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': 'Bearer {0}'.format(token.token)}
        resp = requests.get(self.profile_url, headers=headers)
        extra_data = resp.json()
        return self.get_provider().sociallogin_from_response(request,
                                                             extra_data)


oauth2_login = OAuth2LoginView.adapter_view(StravaOauth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(StravaOauth2Adapter)
