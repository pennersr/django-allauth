from django.conf import settings
from django.utils.decorators import sync_and_async_middleware

from asgiref.sync import iscoroutinefunction

from allauth.core import context
from allauth.core.exceptions import ImmediateHttpResponse


@sync_and_async_middleware
def AccountMiddleware(get_response):
    if iscoroutinefunction(get_response):

        async def middleware(request):
            with context.request_context(request):
                try:
                    response = await get_response(request)
                    _remove_dangling_login(request, response)
                    return response
                except ImmediateHttpResponse as e:
                    return e.response

    else:

        def middleware(request):
            with context.request_context(request):
                try:
                    response = get_response(request)
                    _remove_dangling_login(request, response)
                    return response
                except ImmediateHttpResponse as e:
                    return e.response

    return middleware


def _remove_dangling_login(request, response):
    content_type = response.headers.get("content-type")
    if content_type:
        content_type = content_type.partition(";")[0]
    if content_type and content_type != "text/html":
        return
    if request.path.startswith(settings.STATIC_URL) or request.path in [
        "/favicon.ico",
        "/robots.txt",
        "/humans.txt",
    ]:
        return
    if response.status_code // 100 != 2:
        return
    if not getattr(request, "_account_login_accessed", False):
        if "account_login" in request.session:
            request.session.pop("account_login")
