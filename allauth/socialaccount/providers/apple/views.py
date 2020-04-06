import json
import requests
from datetime import timedelta

from django.http import HttpResponseRedirect
from django.utils import timezone
from django.utils.http import urlencode
from django.views.decorators.csrf import csrf_exempt

import jwt
from requests import HTTPError

from allauth.socialaccount.models import SocialApp, SocialToken
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)
from allauth.utils import get_request_param

from .client import AppleOAuth2Client
from .provider import AppleProvider


class AppleOAuth2Adapter(OAuth2Adapter):
    provider_id = AppleProvider.id
    access_token_url = "https://appleid.apple.com/auth/token"
    authorize_url = "https://appleid.apple.com/auth/authorize"
    public_key_url = "https://appleid.apple.com/auth/keys"

    def _get_apple_public_key(self, kid):
        response = requests.get(self.public_key_url)
        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise OAuth2Error("Error retrieving apple public key.") from e

        for d in data["keys"]:
            if d["kid"] == kid:
                return d

    def get_public_key(self, id_token):
        """
        Get the public key which matches the `kid` in the id_token header.
        """
        kid = jwt.get_unverified_header(id_token)["kid"]
        apple_public_key = self._get_apple_public_key(kid=kid)

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(apple_public_key))
        return public_key

    def get_client_id(self, provider):
        app = SocialApp.objects.get(provider=provider.id)
        return [aud.strip() for aud in app.client_id.split(",")]

    def get_verified_identity_data(self, id_token):
        provider = self.get_provider()
        allowed_auds = self.get_client_id(provider)

        try:
            public_key = self.get_public_key(id_token)
            identity_data = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                verify=True,
                audience=allowed_auds,
                issuer="https://appleid.apple.com",
            )
            return identity_data

        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e

    def parse_token(self, data):
        access_token_data = data["access_token_data"]
        identity_data = data["identity_data"]

        expires_in = access_token_data[self.expires_in_key]
        expires_at = timezone.now() + timedelta(seconds=int(expires_in))

        token = SocialToken(
            token=access_token_data["access_token"],
            token_secret=access_token_data["refresh_token"],
            expires_at=expires_at,
        )
        token.user_data = identity_data
        return token

    def complete_login(self, request, app, token, **kwargs):
        extra_data = token.user_data
        login = self.get_provider().sociallogin_from_response(request=request, response=extra_data)
        login.state["id_token"] = token.user_data
        return login


class AppleOAuth2ClientMixin:
    def get_client(self, request, app):
        client = super().get_client(request, app)
        apple_client = AppleOAuth2Client(
            client.request,
            client.consumer_key,
            client.consumer_secret,
            client.access_token_method,
            client.access_token_url,
            client.callback_url,
            client.scope,
            key=client.key,
            cert=client.cert,
        )
        return apple_client


class AppleOAuth2LoginView(AppleOAuth2ClientMixin, OAuth2LoginView):
    """
    Custom AppleOAuth2LoginView to return AppleOAuth2Client
    """

    pass


class AppleOAuth2CallbackView(AppleOAuth2ClientMixin, OAuth2CallbackView):
    """
    Custom OAuth2CallbackView because `Sign In With Apple`:
        * returns AppleOAuth2Client
        * Apple requests callback by POST
    """

    def get_user_scope_data(self):
        user_scope_data = get_request_param(self.request, "user")
        try:
            return json.loads(user_scope_data)
        except json.JSONDecodeError:
            # We do not care much about user scope data as it maybe blank
            # so return blank dictionary instead
            return {}

    def get_identity_data(self):
        id_token = get_request_param(self.request, "id_token")
        identity_data = self.adapter.get_verified_identity_data(id_token=id_token)
        identity_data["user_scope_data"] = self.get_user_scope_data()
        return identity_data

    def get_token_data(self, app):
        # Parse id_token and other form_post response data
        identity_data = self.get_identity_data()

        # Exchange `code`
        client = self.get_client(self.request, app)
        code = get_request_param(self.request, "code")
        access_token_data = client.get_access_token(code)

        return {
            "identity_data": identity_data,
            "access_token_data": access_token_data
        }


oauth2_login = AppleOAuth2LoginView.adapter_view(AppleOAuth2Adapter)
oauth2_callback = csrf_exempt(AppleOAuth2CallbackView.adapter_view(AppleOAuth2Adapter))
