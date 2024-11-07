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
    from django.conf import settings

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
    # If login is by email, email must be required
    if (
        app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL
        and not app_settings.EMAIL_REQUIRED
    ):
        ret.append(
            Critical(
                msg="ACCOUNT_AUTHENTICATION_METHOD = 'email' requires ACCOUNT_EMAIL_REQUIRED = True"
            )
        )

    # If login includes email, login must be unique
    if (
        app_settings.AUTHENTICATION_METHOD != app_settings.AuthenticationMethod.USERNAME
        and not app_settings.UNIQUE_EMAIL
    ):
        ret.append(
            Critical(
                msg="If ACCOUNT_AUTHENTICATION_METHOD is email based, ACCOUNT_UNIQUE_EMAIL = True is required"
            )
        )

    # Mandatory email verification requires email
    if (
        app_settings.EMAIL_VERIFICATION
        == app_settings.EmailVerificationMethod.MANDATORY
        and not app_settings.EMAIL_REQUIRED
    ):
        ret.append(
            Critical(
                msg="ACCOUNT_EMAIL_VERIFICATION = 'mandatory' requires ACCOUNT_EMAIL_REQUIRED = True"
            )
        )

    if not app_settings.USER_MODEL_USERNAME_FIELD:
        if app_settings.USERNAME_REQUIRED:
            ret.append(
                Critical(
                    msg="No ACCOUNT_USER_MODEL_USERNAME_FIELD, yet, ACCOUNT_USERNAME_REQUIRED = True"
                )
            )

        if app_settings.AUTHENTICATION_METHOD in (
            app_settings.AuthenticationMethod.USERNAME,
            app_settings.AuthenticationMethod.USERNAME_EMAIL,
        ):
            ret.append(
                Critical(
                    msg="No ACCOUNT_USER_MODEL_USERNAME_FIELD, yet, ACCOUNT_AUTHENTICATION_METHOD requires it"
                )
            )

    if (
        app_settings.MAX_EMAIL_ADDRESSES is not None
        and app_settings.MAX_EMAIL_ADDRESSES <= 0
    ):
        ret.append(Critical(msg="ACCOUNT_MAX_EMAIL_ADDRESSES must be None or > 0"))

    if app_settings.CHANGE_EMAIL:
        if (
            app_settings.MAX_EMAIL_ADDRESSES is not None
            and app_settings.MAX_EMAIL_ADDRESSES != 2
        ):
            ret.append(
                Critical(
                    msg="Invalid combination of ACCOUNT_CHANGE_EMAIL and ACCOUNT_MAX_EMAIL_ADDRESSES"
                )
            )
    if hasattr(settings, "ACCOUNT_LOGIN_ATTEMPTS_LIMIT") or hasattr(
        settings, "ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT"
    ):
        ret.append(
            Warning(
                msg="settings.ACCOUNT_LOGIN_ATTEMPTS_LIMIT/TIMEOUT is deprecated, use: settings.ACCOUNT_RATE_LIMITS['login_failed']"
            )
        )

    if hasattr(settings, "ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN"):
        ret.append(
            Warning(
                msg="settings.ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN is deprecated, use: settings.ACCOUNT_RATE_LIMITS['confirm_email']"
            )
        )

    return ret
