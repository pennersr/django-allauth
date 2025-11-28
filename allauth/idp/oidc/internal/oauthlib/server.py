import secrets
import time
import uuid

from django.urls import reverse

import jwt
from oauthlib.oauth2.rfc8628.endpoints import DeviceApplicationServer
from oauthlib.openid import Server

from allauth.core import context
from allauth.core.internal import jwkkit
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib.request_validator import (
    OAuthLibRequestValidator,
)


def generate_opaque_token(request):
    # 160 bit token is recommended, oauthlib uses less.
    # oauch.io -- at oautlib's default, we get:
    #    Out of 11 valid authorization responses, the
    #    average calculated entropy for the access tokens was 144,3 (±7,1) bits
    return secrets.token_urlsafe(64)


def generate_jwt_access_token(request) -> str:
    adapter = get_adapter()
    iat = int(time.time())
    access_token = {
        "client_id": request.client.id,
        "iss": adapter.get_issuer(),
        "iat": iat,
        "exp": iat + app_settings.ACCESS_TOKEN_EXPIRES_IN,
        "jti": uuid.uuid4().hex,
        "token_use": "access",
    }
    # Client credentials has no user.
    if request.user is not None:
        access_token["sub"] = adapter.get_user_sub(request.client, request.user)
    if request.scopes:
        access_token["scope"] = " ".join(request.scopes)
    adapter.populate_access_token(
        access_token, user=request.user, client=request.client, scopes=request.scopes
    )
    jwk_dict, private_key = jwkkit.load_jwk_from_pem(app_settings.PRIVATE_KEY)
    return jwt.encode(
        access_token, private_key, algorithm="RS256", headers={"kid": jwk_dict["kid"]}
    )


def generate_access_token(request) -> str:
    fmt = app_settings.ACCESS_TOKEN_FORMAT
    if fmt == "opaque":
        return generate_opaque_token(request)
    elif fmt == "jwt":
        return generate_jwt_access_token(request)
    else:
        raise ValueError(fmt)


def generate_refresh_token(request) -> str:
    return generate_opaque_token(request)


class OAuthLibServer(Server):
    def __init__(self, **kwargs):
        super().__init__(
            token_generator=generate_access_token,
            refresh_token_generator=generate_refresh_token,
            request_validator=OAuthLibRequestValidator(),
            token_expires_in=app_settings.ACCESS_TOKEN_EXPIRES_IN,
            **kwargs,
        )


class DeviceOAuthLibServer(DeviceApplicationServer):
    def __init__(self):
        verification_uri = context.request.build_absolute_uri(
            reverse("idp:oidc:device_authorization")
        )
        super().__init__(
            request_validator=OAuthLibRequestValidator(),
            verification_uri=verification_uri,
            verification_uri_complete=f"{verification_uri}?code={{user_code}}",
            interval=app_settings.DEVICE_CODE_INTERVAL,
            user_code_generator=lambda: get_adapter().generate_user_code(),
        )
        self._expires_in = app_settings.DEVICE_CODE_EXPIRES_IN


def get_server(**kwargs):
    return OAuthLibServer(**kwargs)


def get_device_server():
    return DeviceOAuthLibServer()
