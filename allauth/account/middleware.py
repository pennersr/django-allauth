from django.conf import settings

from allauth.core import context
from allauth.core.exceptions import ImmediateHttpResponse


class AccountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        with context.request_context(request):
            response = self.get_response(request)
            self._remove_dangling_login(request, response)
            return response

    def process_exception(self, request, exception):
        if isinstance(exception, ImmediateHttpResponse):
            return exception.response

    def _remove_dangling_login(self, request, response):
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
