from importlib import import_module

from django.urls import reverse
from django.conf import settings
from django.utils.cache import patch_vary_headers

APPLE_SESSION_COOKIE_NAME = "apple-login-session"

engine = import_module(settings.SESSION_ENGINE)
SessionStore = engine.SessionStore

def add_apple_session(request):
    """
    Fetch an apple login session
    """
    session_key = request.COOKIES.get(APPLE_SESSION_COOKIE_NAME)
    request.apple_login_session = SessionStore(session_key)

def persist_apple_session(request, response):
    """
    Save `request.apple_login_session` and set the cookie
    """
    patch_vary_headers(response, ('Cookie',))
    request.apple_login_session.save()
    response.set_cookie(
        APPLE_SESSION_COOKIE_NAME,
        request.apple_login_session.session_key,
        max_age=None,
        expires=None,
        domain=settings.SESSION_COOKIE_DOMAIN,
        # The cookie is only needed on this endpoint
        path=reverse("apple_finish_callback"),
        secure=True,
        httponly=None,
        samesite=settings.SESSION_COOKIE_SAMESITE,
    )
