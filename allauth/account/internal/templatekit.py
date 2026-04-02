from typing import Any

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.urls import NoReverseMatch, reverse

from allauth import app_settings as allauth_settings
from allauth.account import app_settings
from allauth.account.utils import passthrough_next_redirect_url


def get_entrance_context_data(request: HttpRequest) -> dict[str, Any]:
    passkey_login_enabled = False
    passkey_signup_enabled = False
    if allauth_settings.MFA_ENABLED:
        from allauth.mfa import app_settings as mfa_settings

        passkey_login_enabled = mfa_settings.PASSKEY_LOGIN_ENABLED
        passkey_signup_enabled = mfa_settings.PASSKEY_SIGNUP_ENABLED

    ret: dict[str, Any] = {}
    signup_url = None
    if not allauth_settings.SOCIALACCOUNT_ONLY:
        try:
            signup_url = passthrough_next_redirect_url(
                request,
                reverse("account_signup"),
                REDIRECT_FIELD_NAME,
            )
        except NoReverseMatch:
            # There may project specific tweaks other than
            # SOCIALACCOUNT_ONLY ...
            pass
    site = get_current_site(request)
    login_url = passthrough_next_redirect_url(
        request,
        reverse("account_login"),
        REDIRECT_FIELD_NAME,
    )

    signup_by_passkey_url = None
    if passkey_signup_enabled:
        signup_by_passkey_url = passthrough_next_redirect_url(
            request,
            reverse("account_signup_by_passkey"),
            REDIRECT_FIELD_NAME,
        )

    ret.update(
        {
            "signup_url": signup_url,
            "signup_by_passkey_url": signup_by_passkey_url,
            "login_url": login_url,
            "site": site,
            "SOCIALACCOUNT_ENABLED": allauth_settings.SOCIALACCOUNT_ENABLED,
            "SOCIALACCOUNT_ONLY": allauth_settings.SOCIALACCOUNT_ONLY,
            "LOGIN_BY_CODE_ENABLED": app_settings.LOGIN_BY_CODE_ENABLED,
            "PASSKEY_LOGIN_ENABLED": passkey_login_enabled,
            "PASSKEY_SIGNUP_ENABLED": passkey_signup_enabled,
        }
    )
    if app_settings.LOGIN_BY_CODE_ENABLED:
        request_login_code_url = passthrough_next_redirect_url(
            request,
            reverse("account_request_login_code"),
            REDIRECT_FIELD_NAME,
        )
        ret["request_login_code_url"] = request_login_code_url
    return ret
