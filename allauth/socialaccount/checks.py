from django.core.checks import Critical, register


@register()
def settings_check(app_configs, **kwargs):
    from allauth import app_settings as allauth_settings
    from allauth.account import app_settings as account_settings
    from allauth.socialaccount import app_settings

    ret = []
    if allauth_settings.SOCIALACCOUNT_ONLY:
        if (
            app_settings.EMAIL_VERIFICATION
            != account_settings.EmailVerificationMethod.NONE
        ):
            ret.append(
                Critical(
                    msg="SOCIALACCOUNT_ONLY requires SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'"
                )
            )
    return ret
