from __future__ import annotations

import posixpath
from http import HTTPStatus
from types import SimpleNamespace

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.urls import NoReverseMatch, reverse
from django.utils.decorators import sync_and_async_middleware

from asgiref.sync import iscoroutinefunction, sync_to_async

from allauth import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal import flows
from allauth.core import context
from allauth.core.exceptions import ImmediateHttpResponse, ReauthenticationRequired
from allauth.core.internal.httpkit import is_headless_request


def _handle_reauthentication_required_on_api(request: HttpRequest):
    if is_headless_request(request):
        from allauth.headless.base.response import ReauthenticationResponse

        return ReauthenticationResponse(request)
    return JsonResponse(status=HTTPStatus.UNAUTHORIZED, data={})


def _handle_reauthentication_required(request: HttpRequest):
    if (
        allauth_settings.HEADLESS_ONLY
        or is_headless_request(request)
        or get_adapter().is_ajax(request)
    ):
        return _handle_reauthentication_required_on_api(request)
    if request.user.is_authenticated:
        methods = get_adapter().get_reauthentication_methods(request.user)
        if not methods:
            raise PermissionDenied
        redirect_url = methods[0]["url"]
    else:
        redirect_url = reverse("account_login")
    return flows.reauthentication.suspend_request(request, redirect_url)


@sync_and_async_middleware
def AccountMiddleware(get_response):
    if iscoroutinefunction(get_response):

        async def async_middleware(request: HttpRequest):
            request.allauth = SimpleNamespace()  # type:ignore[attr-defined]
            with context.request_context(request):
                response = await get_response(request)
                if _should_redirect_accounts(request, response):
                    response = await _aredirect_accounts(request)
                return response

        middleware = async_middleware
    else:

        def sync_middleware(request: HttpRequest):
            request.allauth = SimpleNamespace()  # type:ignore[attr-defined]
            with context.request_context(request):
                response = get_response(request)
                if _should_redirect_accounts(request, response):
                    response = _redirect_accounts(request)
                return response

        middleware = sync_middleware

    def process_exception(request: HttpRequest, exception):
        if isinstance(exception, ImmediateHttpResponse):
            return exception.response
        elif isinstance(exception, ReauthenticationRequired):
            return _handle_reauthentication_required(request)

    middleware.process_exception = process_exception
    return middleware


def _should_redirect_accounts(request: HttpRequest, response) -> bool:
    """
    URLs should be hackable. Yet, assuming allauth is included like this...

        path("accounts/", include("allauth.urls")),

    ... and a user would attempt to navigate to /accounts/, a 404 would be
    presented. This code catches that 404, and redirects to either the email
    management overview or the login page, depending on whether or not the user
    is authenticated.
    """
    if response.status_code != HTTPStatus.NOT_FOUND:
        return False
    try:
        login_path = reverse("account_login")
        email_path = reverse("account_email")
    except NoReverseMatch:
        # Project might have deviated URLs, let's keep out of the way.
        return False
    prefix = posixpath.commonpath([login_path, email_path])
    if prefix == "/" or f"{prefix}/" != request.path:
        return False
    # If we have a prefix that is not just '/', and that is what our request is
    # pointing to, redirect.
    return True


@sync_to_async
def _async_get_user(request: HttpRequest):
    return request.user


async def _aredirect_accounts(request: HttpRequest) -> HttpResponseRedirect:
    email_path = reverse("account_email")
    login_path = reverse("account_login")
    if hasattr(request, "auser"):
        user = await request.auser()
    else:
        # Django <5
        user = await _async_get_user(request)
    return HttpResponseRedirect(email_path if user.is_authenticated else login_path)


def _redirect_accounts(request: HttpRequest) -> HttpResponseRedirect:
    email_path = reverse("account_email")
    login_path = reverse("account_login")
    user = request.user
    return HttpResponseRedirect(email_path if user.is_authenticated else login_path)
