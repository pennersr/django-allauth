from __future__ import annotations

from http import HTTPStatus

from django.http import HttpRequest

from allauth.headless.base.response import APIResponse
from allauth.mfa import app_settings as mfa_settings


def get_config_data(request: HttpRequest) -> dict:
    data = {
        "mfa": {
            "supported_types": mfa_settings.SUPPORTED_TYPES,
            "passkey_login_enabled": mfa_settings.PASSKEY_LOGIN_ENABLED,
        }
    }
    return data


def _authenticator_data(authenticator, sensitive: bool = False) -> dict:
    data = {
        "type": authenticator.type,
        "created_at": authenticator.created_at.timestamp(),
        "last_used_at": (
            authenticator.last_used_at.timestamp()
            if authenticator.last_used_at
            else None
        ),
    }
    if authenticator.type == authenticator.Type.TOTP:
        pass
    elif authenticator.type == authenticator.Type.RECOVERY_CODES:
        wrapped = authenticator.wrap()
        unused_codes = wrapped.get_unused_codes()
        data.update(
            {
                "total_code_count": len(wrapped.generate_codes()),
                "unused_code_count": len(unused_codes),
            }
        )
        if sensitive:
            data["unused_codes"] = unused_codes
    elif authenticator.type == authenticator.Type.WEBAUTHN:
        wrapped = authenticator.wrap()
        data["id"] = authenticator.pk
        data["name"] = wrapped.name
        passwordless = wrapped.is_passwordless
        if passwordless is not None:
            data["is_passwordless"] = passwordless
    return data


class AuthenticatorDeletedResponse(APIResponse):
    pass


class AuthenticatorsDeletedResponse(APIResponse):
    pass


class TOTPNotFoundResponse(APIResponse):
    def __init__(self, request: HttpRequest, secret, totp_url) -> None:
        super().__init__(
            request,
            meta={
                "secret": secret,
                "totp_url": totp_url,
            },
            status=HTTPStatus.NOT_FOUND,
        )


class TOTPResponse(APIResponse):
    def __init__(self, request: HttpRequest, authenticator) -> None:
        data = _authenticator_data(authenticator)
        super().__init__(request, data=data)


class AuthenticatorsResponse(APIResponse):
    def __init__(self, request: HttpRequest, authenticators) -> None:
        data = [_authenticator_data(authenticator) for authenticator in authenticators]
        super().__init__(request, data=data)


class AuthenticatorResponse(APIResponse):
    def __init__(self, request: HttpRequest, authenticator, meta=None) -> None:
        data = _authenticator_data(authenticator)
        super().__init__(request, data=data, meta=meta)


class RecoveryCodesNotFoundResponse(APIResponse):
    def __init__(self, request: HttpRequest) -> None:
        super().__init__(request, status=HTTPStatus.NOT_FOUND)


class RecoveryCodesResponse(APIResponse):
    def __init__(self, request: HttpRequest, authenticator, can_view: bool) -> None:
        data = _authenticator_data(authenticator, sensitive=can_view)
        super().__init__(request, data=data)


class AddWebAuthnResponse(APIResponse):
    def __init__(self, request: HttpRequest, registration_data) -> None:
        super().__init__(request, data={"creation_options": registration_data})


class WebAuthnRequestOptionsResponse(APIResponse):
    def __init__(self, request: HttpRequest, request_options) -> None:
        super().__init__(request, data={"request_options": request_options})
