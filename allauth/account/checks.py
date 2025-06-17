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

    # Often made mistake: ACCOUNT_SIGNUP_FIELDS = [..., "password", ...]
    signup_fields = getattr(settings, "ACCOUNT_SIGNUP_FIELDS", None)
    for wrong_field, right_field in [
        ("password", "password1"),
        ("password*", "password1*"),
    ]:
        if signup_fields and wrong_field in signup_fields:
            ret.append(
                Critical(
                    msg=f"'{wrong_field}' is not a valid field for ACCOUNT_SIGNUP_FIELDS, use '{right_field}'",
                )
            )

    # Cross-check SIGNUP_FIELDS against LOGIN_METHODS. E.g. login is by email, email should be required
    signup_fields = app_settings.SIGNUP_FIELDS
    if not any(
        lm in signup_fields and signup_fields[lm]["required"]
        for lm in app_settings.LOGIN_METHODS
    ):
        ret.append(
            Warning(
                msg="ACCOUNT_LOGIN_METHODS conflicts with ACCOUNT_SIGNUP_FIELDS",
                id="account.W001",
            )
        )

    # If login includes email, email must be unique
    if (
        app_settings.LoginMethod.EMAIL in app_settings.LOGIN_METHODS
        and not app_settings.UNIQUE_EMAIL
    ):
        ret.append(
            Critical(msg="Using email as a login method requires ACCOUNT_UNIQUE_EMAIL")
        )

    # Mandatory email verification requires email
    email_required = "email" in signup_fields and signup_fields["email"]["required"]
    if (
        app_settings.EMAIL_VERIFICATION
        == app_settings.EmailVerificationMethod.MANDATORY
        and not email_required
    ):
        ret.append(
            Critical(
                msg="ACCOUNT_EMAIL_VERIFICATION = 'mandatory' requires 'email*' in ACCOUNT_SIGNUP_FIELDS"
            )
        )

    if not app_settings.USER_MODEL_USERNAME_FIELD:
        if "username" in signup_fields:
            ret.append(
                Critical(
                    msg="No ACCOUNT_USER_MODEL_USERNAME_FIELD, yet, ACCOUNT_SIGNUP_FIELDS contains 'username'"
                )
            )

        if app_settings.LoginMethod.USERNAME in app_settings.LOGIN_METHODS:
            ret.append(
                Critical(
                    msg="No ACCOUNT_USER_MODEL_USERNAME_FIELD, yet, ACCOUNT_LOGIN_METHODS requires it"
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

    if hasattr(settings, "ACCOUNT_AUTHENTICATION_METHOD"):
        converted = set(settings.ACCOUNT_AUTHENTICATION_METHOD.split("_"))
        ret.append(
            Warning(
                f"settings.ACCOUNT_AUTHENTICATION_METHOD is deprecated, use: settings.ACCOUNT_LOGIN_METHODS = {repr(converted)}"
            )
        )

    for field in [
        "ACCOUNT_USERNAME_REQUIRED",
        "ACCOUNT_EMAIL_REQUIRED",
        "ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE",
        "ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE",
    ]:
        if hasattr(settings, field):
            signup_fields_converted = [
                k + ("*" if v["required"] else "")
                for k, v in app_settings.SIGNUP_FIELDS.items()
            ]
            ret.append(
                Warning(
                    f"settings.{field} is deprecated, use: settings.ACCOUNT_SIGNUP_FIELDS = {repr(signup_fields_converted)}"
                )
            )
    return ret
