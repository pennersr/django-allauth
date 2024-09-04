import os
from types import SimpleNamespace

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from django.utils.decorators import sync_and_async_middleware

from asgiref.sync import iscoroutinefunction, sync_to_async

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.internal import flows
from allauth.core import context
from allauth.core.exceptions import (
    ImmediateHttpResponse,
    ReauthenticationRequired,
)


@sync_and_async_middleware
def AccountMiddleware(get_response):
    if iscoroutinefunction(get_response):

        async def middleware(request):
            request.allauth = SimpleNamespace()
            with context.request_context(request):
                response = await get_response(request)
                if _should_check_dangling_login(request, response):
                    await _acheck_dangling_login(request)
                if _should_redirect_accounts(request, response):
                    response = await _aredirect_accounts(request)
                return response

    else:

        def middleware(request):
            request.allauth = SimpleNamespace()
            with context.request_context(request):
                response = get_response(request)
                if _should_check_dangling_login(request, response):
                    _check_dangling_login(request)
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


def _should_check_dangling_login(request, response):
    sec_fetch_dest = request.headers.get("sec-fetch-dest")
    if sec_fetch_dest and sec_fetch_dest != "document":
        return False
    content_type = response.headers.get("content-type")
    if content_type:
        content_type = content_type.partition(";")[0]
    if content_type and content_type != "text/html":
        return False
    # STATIC_URL might be None, as the staticfiles app is not strictly required
    if (
        settings.STATIC_URL and request.path.startswith(settings.STATIC_URL)
    ) or request.path in [
        "/favicon.ico",
        "/robots.txt",
        "/humans.txt",
    ]:
        return False
    if response.status_code // 100 != 2:
        return False
    return True


def _check_dangling_login(request):
    from allauth.account.stages import EmailVerificationStage

    if not getattr(request, "_account_login_accessed", False):
        if login := request.session.get(flows.login.LOGIN_SESSION_KEY):
            if isinstance(login, dict):  # Deal with fake stages
                current_stage = login.get("state", {}).get("stages", {}).get("current")
                if (
                    current_stage == EmailVerificationStage.key
                    and not app_settings.EMAIL_VERIFICATION_BY_CODE_ENABLED
                ):
                    # These days, "email verification by link" is just a regular
                    # stage.  However, "email verification by link" was never
                    # automatically cancelled. So we need to make an exception
                    # here.
                    #
                    # TODO: Reconsider the overall approach to dangling logins:
                    # https://github.com/pennersr/django-allauth/issues/4087
                    return
            request.session.pop(flows.login.LOGIN_SESSION_KEY)


async def _acheck_dangling_login(request):
    await sync_to_async(_check_dangling_login)(request)


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


async def _aredirect_accounts(request) -> HttpResponseRedirect:
    email_path = reverse("account_email")
    login_path = reverse("account_login")
    user = await request.auser()
    return HttpResponseRedirect(email_path if user.is_authenticated else login_path)


def _redirect_accounts(request) -> HttpResponseRedirect:
    email_path = reverse("account_email")
    login_path = reverse("account_login")
    user = request.user
    return HttpResponseRedirect(email_path if user.is_authenticated else login_path)
