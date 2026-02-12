from functools import wraps

from django.contrib.auth.decorators import login_required

from .authz import require_app_access


def app_permission(app_name: str):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            require_app_access(request, app_name)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
