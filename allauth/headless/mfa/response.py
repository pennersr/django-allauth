from allauth.headless.base.response import APIResponse
from allauth.mfa import app_settings, totp


def get_config_data(request):
    data = {"mfa": {"supported_types": app_settings.SUPPORTED_TYPES}}
    return data


def respond_totp_inactive(request):
    secret = totp.get_totp_secret(regenerate=True)
    return APIResponse(
        data={
            "secret": secret,
        },
        status=404,
    )


def respond_totp_active(request, totp):
    return APIResponse()


def respond_authenticator_list(request, authenticators):
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
    return APIResponse(data=entries)


def respond_recovery_codes_inactive(request):
    return APIResponse(
        status=404,
    )


def respond_recovery_codes_active(request, recovery_codes):
    wrapped = recovery_codes.wrap()
    unused_codes = wrapped.get_unused_codes()
    data = {
        "total_code_count": len(wrapped.generate_codes()),
        "unused_code_count": len(unused_codes),
        "unused_codes": unused_codes,
    }
    return APIResponse(data=data)
