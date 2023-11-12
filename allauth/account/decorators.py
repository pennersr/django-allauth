from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.reauthentication import (
    did_recently_authenticate,
    suspend_request,
)
from allauth.account.utils import send_email_confirmation


def verified_email_required(
    function=None, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME
):
    """
    Even when email verification is not mandatory during signup, there
    may be circumstances during which you really want to prevent
    unverified users to proceed. This decorator ensures the user is
    authenticated and has a verified email address. If the former is
    not the case then the behavior is identical to that of the
    standard `login_required` decorator. If the latter does not hold,
    email verification mails are automatically resend and the user is
    presented with a page informing them they needs to verify their email
    address.
    """

    def decorator(view_func):
        @login_required(redirect_field_name=redirect_field_name, login_url=login_url)
        def _wrapped_view(request, *args, **kwargs):
            if not EmailAddress.objects.filter(
                user=request.user, verified=True
            ).exists():
                send_email_confirmation(request, request.user)
                return render(request, "account/verified_email_required.html")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)
    return decorator


def reauthentication_required(
    function=None,
    redirect_field_name=REDIRECT_FIELD_NAME,
    allow_get=False,
    enabled=None,
):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            pass_method = allow_get and request.method == "GET"
            ena = (enabled is None) or (
                enabled(request) if callable(enabled) else enabled
            )
            if ena and not pass_method:
                if request.user.is_anonymous or not did_recently_authenticate(request):
                    redirect_url = reverse("account_login")
                    methods = get_adapter().get_reauthentication_methods(request.user)
                    if methods:
                        redirect_url = methods[0]["url"]
                    return suspend_request(request, redirect_url)
            return view_func(request, *args, **kwargs)

        return _wrapper_view

    if function:
        return decorator(function)
    return decorator
