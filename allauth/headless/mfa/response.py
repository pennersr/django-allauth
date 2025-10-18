from http import HTTPStatus

from allauth.headless.base.response import APIResponse
from allauth.mfa import app_settings as mfa_settings


def get_config_data(request):
    data = {
        "mfa": {
            "supported_types": mfa_settings.SUPPORTED_TYPES,
            "passkey_login_enabled": mfa_settings.PASSKEY_LOGIN_ENABLED,
        }
    }
    return data


def _authenticator_data(authenticator, sensitive=False):
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
    def __init__(self, request, secret, totp_url):
        super().__init__(
            request,
            meta={
                "secret": secret,
                "totp_url": totp_url,
            },
            status=HTTPStatus.NOT_FOUND,
        )


class TOTPResponse(APIResponse):
    def __init__(self, request, authenticator):
        data = _authenticator_data(authenticator)
        super().__init__(request, data=data)


class AuthenticatorsResponse(APIResponse):
    def __init__(self, request, authenticators):
        data = [_authenticator_data(authenticator) for authenticator in authenticators]
        super().__init__(request, data=data)


class AuthenticatorResponse(APIResponse):
    def __init__(self, request, authenticator, meta=None):
        data = _authenticator_data(authenticator)
        super().__init__(request, data=data, meta=meta)


class RecoveryCodesNotFoundResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=HTTPStatus.NOT_FOUND)


class RecoveryCodesResponse(APIResponse):
    def __init__(self, request, authenticator):
        data = _authenticator_data(authenticator, sensitive=True)
        super().__init__(request, data=data)


class AddWebAuthnResponse(APIResponse):
    def __init__(self, request, registration_data):
        super().__init__(request, data={"creation_options": registration_data})


class WebAuthnRequestOptionsResponse(APIResponse):
    def __init__(self, request, request_options):
        super().__init__(request, data={"request_options": request_options})
