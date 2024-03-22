from importlib import import_module

from django.conf import settings


def session_token_to_key(token):
    return token


def session_key_to_token(key):
    return key


def get_session_store():
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore


def new_session():
    return get_session_store()(None)


def has_session_token(request):
    return bool(request.headers.get("x-session-token"))


def get_session(request):
    token = request.headers.get("x-session-token")
    if not token:
        return None
    store = get_session_store()
    key = session_token_to_key(token)
    if not store().exists(key):
        return None
    session = store(key)
    return session


def expose_session_token(request):
    token = request.headers.get("x-session-token")
    header_key = None
    if token:
        header_key = session_token_to_key(token)
    modified = request.session.modified
    if modified and (not header_key or header_key != request.session.session_key):
        return session_key_to_token(request.session.session_key)
