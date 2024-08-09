from django.core.checks import Critical, Warning, register


@register()
def adapter_check(app_configs, **kwargs):
    from allauth.account.adapter import get_adapter

    ret = []
    adapter = get_adapter()
    if hasattr(adapter, "get_email_confirmation_redirect_url"):
        ret.append(
            Warning(
                msg="adapter.get_email_confirmation_redirect_url(request) is deprecated, use adapter.get_email_verification_redirect_url(email_address)"
            )
        )
    return ret


@register()
def settings_check(app_configs, **kwargs):
    from allauth import app_settings as allauth_app_settings
    from allauth.account import app_settings

    ret = []
    if allauth_app_settings.SOCIALACCOUNT_ONLY:
        if app_settings.LOGIN_BY_CODE_ENABLED:
            ret.append(
                Critical(
                    msg="SOCIALACCOUNT_ONLY does not work with ACCOUNT_LOGIN_BY_CODE_ENABLED"
                )
            )
        if allauth_app_settings.MFA_ENABLED:
            ret.append(
                Critical(msg="SOCIALACCOUNT_ONLY does not work with 'allauth.mfa'")
            )
        if app_settings.EMAIL_VERIFICATION != app_settings.EmailVerificationMethod.NONE:
            ret.append(
                Critical(
                    msg="SOCIALACCOUNT_ONLY requires ACCOUNT_EMAIL_VERIFICATION = 'none'"
                )
            )
    if (
        app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED
        and app_settings.EMAIL_VERIFICATION
        != app_settings.EmailVerificationMethod.MANDATORY
    ):
        ret.append(
            Critical(
                msg="ACCOUNT_EMAIL_VERFICATION_BY_CODE requires ACCOUNT_EMAIL_VERIFICATION = 'mandatory'"
            )
        )
    return ret
