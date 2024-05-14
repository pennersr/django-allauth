from allauth.headless.base.response import APIResponse
from allauth.mfa import app_settings


def get_config_data(request):
    data = {"mfa": {"supported_types": app_settings.SUPPORTED_TYPES}}
    return data


def _authenticator_data(authenticator, sensitive=False):
    data = {
        "type": authenticator.type,
        "created_at": authenticator.created_at.timestamp(),
        "last_used_at": authenticator.last_used_at.timestamp()
        if authenticator.last_used_at
        else None,
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
    return data


class AuthenticatorDeletedResponse(APIResponse):
    pass


class TOTPNotFoundResponse(APIResponse):
    def __init__(self, request, secret):
        super().__init__(
            request,
            meta={
                "secret": secret,
            },
            status=404,
        )


class TOTPResponse(APIResponse):
    def __init__(self, request, authenticator):
        data = _authenticator_data(authenticator)
        super().__init__(request, data=data)


class AuthenticatorsResponse(APIResponse):
    def __init__(self, request, authenticators):
        data = [_authenticator_data(authenticator) for authenticator in authenticators]
        super().__init__(request, data=data)


class RecoveryCodesNotFoundResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=404)


class RecoveryCodesResponse(APIResponse):
    def __init__(self, request, authenticator):
        data = _authenticator_data(authenticator, sensitive=True)
        super().__init__(request, data=data)
