from __future__ import annotations

import secrets
import time
import uuid
from typing import Any

from django.urls import reverse

from oauthlib.common import Request
from oauthlib.oauth2.rfc6749 import errors
from oauthlib.oauth2.rfc8628.endpoints import DeviceApplicationServer
from oauthlib.openid import Server

from allauth.core import context
from allauth.core.internal import jwkkit
from allauth.core.internal.deferred import jwt
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib import authorization_codes
from allauth.idp.oidc.internal.oauthlib.request_validator import (
    OAuthLibRequestValidator,
)
from allauth.idp.oidc.internal.oauthlib.utils import get_validator_context


def generate_opaque_token(request: Request) -> str:
    # 160 bit token is recommended, oauthlib uses less.
    # oauch.io -- at oautlib's default, we get:
    #    Out of 11 valid authorization responses, the
    #    average calculated entropy for the access tokens was 144,3 (±7,1) bits
    return secrets.token_urlsafe(64)


def generate_jwt_access_token(request: Request) -> str:
    adapter = get_adapter()
    iat = int(time.time())
    access_token = {
        "client_id": request.client.id,
        "iss": adapter.get_issuer(),
        "iat": iat,
        "exp": iat + app_settings.ACCESS_TOKEN_EXPIRES_IN,
        "jti": uuid.uuid4().hex,
        "token_use": "access",  # nosec
    }
    # Client credentials has no user.
    ctx = get_validator_context()
    resources = ctx.requested_resources or ctx.granted_resources
    if resources:
        access_token["aud"] = resources
    if request.user is not None:
        access_token["sub"] = adapter.get_user_sub(request.client, request.user)
    if request.scopes:
        access_token["scope"] = " ".join(request.scopes)
    adapter.populate_access_token(
        access_token, user=request.user, client=request.client, scopes=request.scopes
    )
    jwk_dict, private_key = jwkkit.load_jwk_from_pem(adapter.get_signing_key().pem)
    return jwt.encode(
        access_token, private_key, algorithm="RS256", headers={"kid": jwk_dict["kid"]}
    )


def generate_access_token(request: Request) -> str:
    fmt = app_settings.ACCESS_TOKEN_FORMAT
    if fmt == "opaque":
        return generate_opaque_token(request)
    elif fmt == "jwt":
        return generate_jwt_access_token(request)
    else:
        raise ValueError(fmt)


def generate_refresh_token(request: Request) -> str:
    return generate_opaque_token(request)


def validate_code_challenge_method(request: Request) -> dict:
    if request.code_challenge is not None and request.code_challenge_method != "S256":
        raise errors.UnsupportedCodeChallengeMethodError(request=request)
    return {}


def claim_authorization_code(request: Request) -> None:
    if not authorization_codes.claim(request.client_id, request.code, request):
        raise errors.InvalidGrantError(request=request)


class OAuthLibServer(Server):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            token_generator=generate_access_token,
            refresh_token_generator=generate_refresh_token,
            request_validator=OAuthLibRequestValidator(),
            token_expires_in=app_settings.ACCESS_TOKEN_EXPIRES_IN,
            **kwargs,
        )
        for grant in (
            self.auth_grant,
            self.openid_connect_auth,
            self.openid_connect_hybrid,
        ):
            grant.custom_validators.pre_auth.append(validate_code_challenge_method)
        for grant in (self.auth_grant, self.openid_connect_auth):
            grant.custom_validators.post_token.append(claim_authorization_code)


class DeviceOAuthLibServer(DeviceApplicationServer):
    def __init__(self) -> None:
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


def get_server(**kwargs: Any) -> OAuthLibServer:
    return OAuthLibServer(**kwargs)


def get_device_server() -> DeviceOAuthLibServer:
    return DeviceOAuthLibServer()
