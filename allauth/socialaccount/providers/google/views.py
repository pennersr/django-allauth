import requests

from django.conf import settings

import jwt

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from .provider import GoogleProvider


IDENTITY_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("IDENTITY_URL", "https://www.googleapis.com/oauth2/v2/userinfo")
)

ACCESS_TOKEN_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ACCESS_TOKEN_URL", "https://oauth2.googleapis.com/token")
)

AUTHORIZE_URL = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("AUTHORIZE_URL", "https://accounts.google.com/o/oauth2/v2/auth")
)

ID_TOKEN_ISSUER = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("ID_TOKEN_ISSUER", "https://accounts.google.com")
)

FETCH_USERINFO = (
    getattr(settings, "SOCIALACCOUNT_PROVIDERS", {})
    .get("google", {})
    .get("FETCH_USERINFO", False)
)


class GoogleOAuth2Adapter(OAuth2Adapter):
    provider_id = GoogleProvider.id
    access_token_url = ACCESS_TOKEN_URL
    authorize_url = AUTHORIZE_URL
    id_token_issuer = ID_TOKEN_ISSUER
    identity_url = IDENTITY_URL
    fetch_userinfo = FETCH_USERINFO

    def complete_login(self, request, app, token, response, **kwargs):
        data = None
        id_token = response.get("id_token")
        if id_token:
            data = self._decode_id_token(app, id_token)
            if self.fetch_userinfo and "picture" not in data:
                info = self._fetch_user_info(token.token)
                picture = info.get("picture")
                if picture:
                    data["picture"] = picture
        else:
            data = self._fetch_user_info(token.token)
        login = self.get_provider().sociallogin_from_response(request, data)
        return login

    def _decode_id_token(self, app, id_token):
        try:
            data = jwt.decode(
                id_token,
                # Since the token was received by direct communication
                # protected by TLS between this library and Google, we
                # are allowed to skip checking the token signature
                # according to the OpenID Connect Core 1.0
                # specification.
                # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
                options={
                    "verify_signature": False,
                    "verify_iss": True,
                    "verify_aud": True,
                    "verify_exp": True,
                },
                issuer=self.id_token_issuer,
                audience=app.client_id,
            )
        except jwt.PyJWTError as e:
            raise OAuth2Error("Invalid id_token") from e
        return data

    def _fetch_user_info(self, access_token):
        resp = requests.get(
            self.identity_url,
            headers={"Authorization": "Bearer {}".format(access_token)},
        )
        if not resp.ok:
            raise OAuth2Error("Request to user info failed")
        return resp.json()


oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2Adapter)
