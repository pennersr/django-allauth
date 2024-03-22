from functools import wraps
from types import SimpleNamespace

from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

from allauth.headless.constants import Client
from allauth.headless.internal import authkit


def mark_request_as_headless(request, client):
    request.allauth.headless = SimpleNamespace()
    request.allauth.headless.client = client


def app_view(
    function=None,
):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            mark_request_as_headless(request, Client.APP)
            with authkit.authentication_context(request):
                return view_func(request, *args, **kwargs)

        return _wrapper_view

    ret = decorator
    if function:
        ret = decorator(function)
    return csrf_exempt(ret)


def browser_view(
    function=None,
):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapper_view(request, *args, **kwargs):
            mark_request_as_headless(request, Client.BROWSER)
            # Needed -- so that the CSRF token is set in the response for the
            # frontend to pick up.
            get_token(request)
            return view_func(request, *args, **kwargs)

        return _wrapper_view

    ret = decorator
    if function:
        ret = decorator(function)
    return ret
