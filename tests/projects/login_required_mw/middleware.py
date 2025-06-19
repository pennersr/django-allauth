from django.contrib.auth.middleware import LoginRequiredMiddleware


class CustomLoginRequiredMiddleware(LoginRequiredMiddleware):
    def handle_no_permission(self, request, view_func):
        # Quick & dirty workaround for: https://github.com/vitalik/django-ninja/issues/1461
        if "ninja.operation.PathView" in repr(view_func):
            return None
        return super().handle_no_permission(request, view_func)
