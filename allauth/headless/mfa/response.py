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
