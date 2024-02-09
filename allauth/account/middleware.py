from django.conf import settings
from django.utils.decorators import sync_and_async_middleware

from asgiref.sync import iscoroutinefunction, sync_to_async

from allauth.core import context
from allauth.core.exceptions import ImmediateHttpResponse


@sync_and_async_middleware
def AccountMiddleware(get_response):
    if iscoroutinefunction(get_response):

        async def middleware(request):
            with context.request_context(request):
                try:
                    response = await get_response(request)
                    if _should_check_dangling_login(request, response):
                        await _acheck_dangling_login(request)
                    return response
                except ImmediateHttpResponse as e:
                    return e.response

    else:

        def middleware(request):
            with context.request_context(request):
                try:
                    response = get_response(request)
                    if _should_check_dangling_login(request, response):
                        _check_dangling_login(request)
                    return response
                except ImmediateHttpResponse as e:
                    return e.response

    return middleware


def _should_check_dangling_login(request, response):
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
