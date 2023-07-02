from importlib import import_module
from urllib.parse import urlparse

from django.conf import settings
from django.utils.cache import patch_vary_headers


engine = import_module(settings.SESSION_ENGINE)
SessionStore = engine.SessionStore


class LoginSession:
    """Some providers sometimes POST their responses, which due to
    CORS/Samesite-cookie rules means that this request cannot access the session
    as its session cookie is unavailable.

    We work around this by storing the response in a separate, temporary session
    and redirecting to a different endpoint that can pick up the flow.
    """

    def __init__(self, request, attribute_name, cookie_name):
        """
        Prepares an provider specific session.
        """
        self.request = request
        self.attribute_name = attribute_name
        self.cookie_name = cookie_name
        self.store = getattr(request, attribute_name, None)
        if self.store is None:
            session_key = request.COOKIES.get(cookie_name)
            self.store = SessionStore(session_key)
            setattr(request, attribute_name, self.store)

    def save(self, response):
        """
        Save the session and set a cookie.
        """
        patch_vary_headers(response, ("Cookie",))
        self.store.save()
        kwargs = {}
        samesite = getattr(settings, "SESSION_COOKIE_SAMESITE", None)
        if samesite:
            kwargs["samesite"] = samesite
        response.set_cookie(
            self.cookie_name,
            self.store.session_key,
            max_age=None,
            expires=None,
            domain=settings.SESSION_COOKIE_DOMAIN,
            # The cookie is only needed on this endpoint
            path=urlparse(response.url).path,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=None,
            **kwargs
        )

    def delete(self):
        self.store.delete()
