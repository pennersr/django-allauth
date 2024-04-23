from django.core.checks import Critical, register


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
                    msg="SOCIALACCOUNT_ONLY requires ACCOUNT_EMAIL_VERIFICATION_METHOD = 'none'"
                )
            )
    return ret
