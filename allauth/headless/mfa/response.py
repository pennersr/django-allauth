from allauth.headless.base.response import APIResponse
from allauth.mfa import app_settings


def get_config_data(request):
    data = {"mfa": {"supported_types": app_settings.SUPPORTED_TYPES}}
    return data


class AuthenticatorDeletedResponse(APIResponse):
    pass


class TOTPNotFoundResponse(APIResponse):
    def __init__(self, request, secret):
        super().__init__(
            request,
            data={
                "secret": secret,
            },
            status=404,
        )


class TOTPResponse(APIResponse):
    def __init__(self, request, authenticator):
        super().__init__(request)


class AuthenticatorsResponse(APIResponse):
    def __init__(self, request, authenticators):
        entries = []
        for authenticator in authenticators:
            entry = {"type": authenticator.type}
            wrapped = authenticator.wrap()
            if authenticator.type == authenticator.Type.TOTP:
                pass
            elif authenticator.type == authenticator.Type.RECOVERY_CODES:
                entry.update(
                    {
                        "total_code_count": len(wrapped.generate_codes()),
                        "unused_code_count": len(wrapped.get_unused_codes()),
                    }
                )
            entries.append(entry)
        super().__init__(request, data=entries)


class RecoveryCodesNotFoundResponse(APIResponse):
    def __init__(self, request):
        super().__init__(request, status=404)


class RecoveryCodesResponse(APIResponse):
    def __init__(self, request, authenticator):
        wrapped = authenticator.wrap()
        unused_codes = wrapped.get_unused_codes()
        data = {
            "total_code_count": len(wrapped.generate_codes()),
            "unused_code_count": len(unused_codes),
            "unused_codes": unused_codes,
        }
        super().__init__(request, data=data)
