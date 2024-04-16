# from time import sleep

# import jwt

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from allauth.socialaccount.models import SocialToken
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import jwtkit


from .provider import XeroProvider

from django.utils import timezone


class XeroOAuth2Adapter(OAuth2Adapter):
    provider_id = XeroProvider.id
    access_token_url = "https://identity.xero.com/connect/token"
    refresh_token_url = "https://identity.xero.com/connect/token"
    authorize_url = "https://login.xero.com/identity/connect/authorize"
    profile_url = "https://api.xero.com/api.xro/2.0/Users"

    public_key_url = (
        "https://identity.xero.com/.well-known/openid-configuration/jwks"
    )

    tenants_url = "https://api.xero.com/connections"

    def get_verified_identity_data(self, id_token):
        app = get_adapter().get_app(request=None, provider=self.provider_id)
        data = jwtkit.verify_and_decode(
            credential=id_token,
            keys_url=self.public_key_url,
            issuer="https://identity.xero.com",
            audience=app.client_id,
            lookup_kid=jwtkit.lookup_kid_jwk,
        )
        return data

    def parse_token(self, data):
        token = SocialToken(
            token=data["access_token"],
        )
        token.token_secret = data.get("refresh_token", "")

        expires_in = data.get(self.expires_in_key)
        if expires_in:
            token.expires_at = timezone.now() + timezone.timedelta(
                seconds=int(expires_in)
            )

        # `user_data` is a big flat dictionary with the parsed JWT claims
        # access_tokens, and user info from the apple post.
        identity_data = self.get_verified_identity_data(data["id_token"])
        token.user_data = {**data, **identity_data}

        return token

    def complete_login(self, request, app, token, **kwargs):
        extra_data = token.user_data
        login = self.get_provider().sociallogin_from_response(
            request=request, response=extra_data
        )
        login.state["id_token"] = token.user_data
        return login


oauth2_login = OAuth2LoginView.adapter_view(XeroOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(XeroOAuth2Adapter)
