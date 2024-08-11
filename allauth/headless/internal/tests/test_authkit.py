from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
)
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse

from allauth.headless.internal.authkit import purge_request_user_cache


def test_purge_request_user_cache(rf, user):
    request = rf.get("/")
    smw = SessionMiddleware(lambda request: HttpResponse())
    smw(request)
    amw = AuthenticationMiddleware(lambda request: HttpResponse())
    amw(request)
    assert request.user.is_anonymous
    assert not request.user.pk
    purge_request_user_cache(request)
    request.session[SESSION_KEY] = user.pk
    request.session[BACKEND_SESSION_KEY] = (
        "allauth.account.auth_backends.AuthenticationBackend"
    )
    request.session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    assert request.user.is_authenticated
    assert request.user.pk == user.pk
