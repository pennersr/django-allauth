import os
from types import SimpleNamespace

from django.http import HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from django.utils.decorators import sync_and_async_middleware

from asgiref.sync import iscoroutinefunction, sync_to_async

from allauth.account.adapter import get_adapter
from allauth.account.internal import flows
from allauth.core import context
from allauth.core.exceptions import ImmediateHttpResponse, ReauthenticationRequired


@sync_and_async_middleware
def AccountMiddleware(get_response):
    if iscoroutinefunction(get_response):

        async def middleware(request):
            request.allauth = SimpleNamespace()
            with context.request_context(request):
                response = await get_response(request)
                if _should_redirect_accounts(request, response):
                    response = await _aredirect_accounts(request)
                return response

    else:

        def middleware(request):
            request.allauth = SimpleNamespace()
            with context.request_context(request):
                response = get_response(request)
                if _should_redirect_accounts(request, response):
                    response = _redirect_accounts(request)
                return response

    def process_exception(request, exception):
        if isinstance(exception, ImmediateHttpResponse):
            return exception.response
        elif isinstance(exception, ReauthenticationRequired):
            redirect_url = reverse("account_login")
            methods = get_adapter().get_reauthentication_methods(request.user)
            if methods:
                redirect_url = methods[0]["url"]
            return flows.reauthentication.suspend_request(request, redirect_url)

    middleware.process_exception = process_exception
    return middleware


def _should_redirect_accounts(request, response) -> bool:
    """
    URLs should be hackable. Yet, assuming allauth is included like this...

        path("accounts/", include("allauth.urls")),

    ... and a user would attempt to navigate to /accounts/, a 404 would be
    presented. This code catches that 404, and redirects to either the email
    management overview or the login page, depending on whether or not the user
    is authenticated.
    """
    if response.status_code != 404:
        return False
    try:
        login_path = reverse("account_login")
        email_path = reverse("account_email")
    except NoReverseMatch:
        # Project might have deviated URLs, let's keep out of the way.
        return False
    prefix = os.path.commonprefix([login_path, email_path])
    if len(prefix) <= 1 or prefix != request.path:
        return False
    # If we have a prefix that is not just '/', and that is what our request is
    # pointing to, redirect.
    return True


@sync_to_async
def _async_get_user(request):
    return request.user


async def _aredirect_accounts(request) -> HttpResponseRedirect:
    email_path = reverse("account_email")
    login_path = reverse("account_login")
    if hasattr(request, "auser"):
        user = await request.auser()
    else:
        # Django <5
        user = await _async_get_user(request)
    return HttpResponseRedirect(email_path if user.is_authenticated else login_path)


def _redirect_accounts(request) -> HttpResponseRedirect:
    email_path = reverse("account_email")
    login_path = reverse("account_login")
    user = request.user
    return HttpResponseRedirect(email_path if user.is_authenticated else login_path)
