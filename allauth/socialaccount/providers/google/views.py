import requests

import jwt

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import GoogleProvider


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = "https://oauth2.googleapis.com/token"
    authorize_url = "https://accounts.google.com/o/oauth2/v2/auth"

    def complete_login(self, request, app, token, response, **kwargs):
        identity_data = jwt.decode(
            response["id_token"],
            # We are sure that the token was received in a response from
            # Google, so we skip requesting keys for verifying the
            # signature.
            options={"verify_signature": False},
            audience=app.client_id,
        )
        login = self.get_provider().sociallogin_from_response(request, identity_data)
        return login


oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
