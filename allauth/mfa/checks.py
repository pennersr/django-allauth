from django.core.checks import Critical, register


@register()
def settings_check(app_configs, **kwargs):
    from allauth.account import app_settings as account_settings
    from allauth.mfa import app_settings
    from allauth.mfa.models import Authenticator

    ret = []
    if app_settings.PASSKEY_SIGNUP_ENABLED:
        if Authenticator.Type.WEBAUTHN not in app_settings.SUPPORTED_TYPES:
            ret.append(
                Critical(
                    msg="MFA_PASSKEY_SIGNUP_ENABLED requires MFA_SUPPORTED_TYPES to include 'webauthn'"
                )
            )
        if not account_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED:
            # The fact that a signup is passkey based is stored in the session,
            # which gets lost when using link based verification.
            ret.append(
                Critical(
                    msg="MFA_PASSKEY_SIGNUP_ENABLED requires ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED"
                )
            )
        email_required = account_settings.SIGNUP_FIELDS.get("email", {}).get("required")
        if not email_required:
            ret.append(
                Critical(
                    msg="MFA_PASSKEY_SIGNUP_ENABLED requires ACCOUNT_SIGNUP_FIELDS to contain 'email*'"
                )
            )
        if (
            account_settings.EMAIL_VERIFICATION
            != account_settings.EmailVerificationMethod.MANDATORY
        ):
            ret.append(
                Critical(
                    msg="MFA_PASSKEY_SIGNUP_ENABLED requires ACCOUNT_EMAIL_VERIFICATION = 'mandatory'"
                )
            )
    return ret
