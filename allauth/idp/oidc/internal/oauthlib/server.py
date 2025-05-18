import secrets

from django.urls import reverse

from oauthlib.oauth2.rfc8628.endpoints import DeviceApplicationServer
from oauthlib.openid import Server

from allauth.core import context
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib.request_validator import (
    OAuthLibRequestValidator,
)


def generate_token(request) -> str:
    # oauch.io -- at oautlib's default, we get:
    #    Out of 11 valid authorization responses, the
    #    average calculated entropy for the access tokens was 144,3 (±7,1) bits
    return secrets.token_urlsafe(64)


class OAuthLibServer(Server):
    def __init__(self, **kwargs):
        super().__init__(
            # 160 bit token is recommended, oauthlib uses less.
            token_generator=generate_token,
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
            verification_uri_complete=verification_uri + "?code={user_code}",
            interval=app_settings.DEVICE_CODE_INTERVAL,
            user_code_generator=lambda: get_adapter().generate_user_code(),
        )
        self._expires_in = app_settings.DEVICE_CODE_EXPIRES_IN


def get_server(**kwargs):
    return OAuthLibServer(**kwargs)


def get_device_server():
    return DeviceOAuthLibServer()
