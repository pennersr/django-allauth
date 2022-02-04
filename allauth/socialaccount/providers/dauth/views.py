import requests
import datetime

from allauth.socialaccount.providers.oauth2.views import (OAuth2Adapter,
                                                          OAuth2LoginView,
                                                          OAuth2CallbackView)
from allauth.socialaccount.models import SocialToken

from .provider import DAuthProvider


class DAuthAdapter(OAuth2Adapter):
    provider_id = DAuthProvider.id
    authorize_url = "https://auth.delta.nitt.edu/authorize"
    access_token_url = "https://auth.delta.nitt.edu/api/oauth/token"
    profile_url = "https://auth.delta.nitt.edu/api/resources/user"

    def parse_token(self, data):
        token = SocialToken(token=data["access_token"])
        token.token_secret = data.get("refresh_token", "")
        token.expires_at = datetime.datetime.fromtimestamp(data["expires_in"] / 1000.0)
        return token

    # After successfully logging in, use access token to retrieve user info
    def complete_login(self, request, app, token, **kwargs):
        resp = requests.post(self.profile_url, data={"access_token": token.token})
        resp.raise_for_status()
        return self.get_provider().sociallogin_from_response(request, resp.json())


oauth2_login = OAuth2LoginView.adapter_view(DAuthAdapter)
oauth2_callback = OAuth2CallbackView.adapter_view(DAuthAdapter)
