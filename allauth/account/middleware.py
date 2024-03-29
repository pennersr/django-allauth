from django.conf import settings
from django.urls import reverse
from django.utils.decorators import sync_and_async_middleware

from asgiref.sync import iscoroutinefunction, sync_to_async

from allauth.account.adapter import get_adapter
from allauth.account.reauthentication import suspend_request
from allauth.core import context
from allauth.core.exceptions import (
    ImmediateHttpResponse,
    ReauthenticationRequired,
)


@sync_and_async_middleware
def AccountMiddleware(get_response):
    if iscoroutinefunction(get_response):

        async def middleware(request):
            with context.request_context(request):
                response = await get_response(request)
                if _should_check_dangling_login(request, response):
                    await _acheck_dangling_login(request)
                return response

    else:

        def middleware(request):
            with context.request_context(request):
                response = get_response(request)
                if _should_check_dangling_login(request, response):
                    _check_dangling_login(request)
                return response

    def process_exception(request, exception):
        if isinstance(exception, ImmediateHttpResponse):
            return exception.response
        elif isinstance(exception, ReauthenticationRequired):
            redirect_url = reverse("account_login")
            methods = get_adapter().get_reauthentication_methods(request.user)
            if methods:
                redirect_url = methods[0]["url"]
            return suspend_request(request, redirect_url)

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
    if request.path.startswith(settings.STATIC_URL) or request.path in [
        "/favicon.ico",
        "/robots.txt",
        "/humans.txt",
    ]:
        return False
    if response.status_code // 100 != 2:
        return False
    return True


def _check_dangling_login(request):
    if not getattr(request, "_account_login_accessed", False):
        if "account_login" in request.session:
            request.session.pop("account_login")


async def _acheck_dangling_login(request):
    await sync_to_async(_check_dangling_login)(request)
