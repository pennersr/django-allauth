from http import HTTPStatus

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from allauth import app_settings as allauth_settings
from allauth.account import app_settings as account_settings
from allauth.account.utils import user_display
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.internal import flows
from allauth.socialaccount.providers.base import AuthError


def render_authentication_error(
    request,
    provider,
    error=AuthError.UNKNOWN,
    exception=None,
    extra_context=None,
):
    try:
        if extra_context is None:
            extra_context = {}
        get_adapter().on_authentication_error(
            request,
            provider,
            error=error,
            exception=exception,
            extra_context=extra_context,
        )
        if allauth_settings.HEADLESS_ENABLED:
            from allauth.headless.socialaccount import internal

            internal.on_authentication_error(
                request,
                provider=provider,
                error=error,
                exception=exception,
                extra_context=extra_context,
            )

    except ImmediateHttpResponse as e:
        return e.response
    if error == AuthError.CANCELLED:
        return HttpResponseRedirect(reverse("socialaccount_login_cancelled"))
    context = {
        "auth_error": {
            "provider": provider,
            "code": error,
            "exception": exception,
        }
    }
    context.update(extra_context)
    return render(
        request,
        f"socialaccount/authentication_error.{account_settings.TEMPLATE_EXTENSION}",
        context,
        status=HTTPStatus.UNAUTHORIZED,
    )


def complete_social_login(request, sociallogin):
    if sociallogin.is_headless:
        from allauth.headless.socialaccount import internal

        return internal.complete_login(request, sociallogin)
    return flows.login.complete_login(request, sociallogin)


def socialaccount_user_display(socialaccount):
    func = app_settings.SOCIALACCOUNT_STR
    if not func:
        return user_display(socialaccount.user)
    return func(socialaccount)
