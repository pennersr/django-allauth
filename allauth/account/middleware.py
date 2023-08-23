from django.conf import settings


class AccountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        response = self.get_response(request)
        self._remove_dangling_login(request, response)
        return response

    def _remove_dangling_login(self, request, response):
        if request.path.startswith(settings.STATIC_URL):
            return
        if not getattr(request, "_account_login_accessed", False):
            if "account_login" in request.session:
                request.session.pop("account_login")
