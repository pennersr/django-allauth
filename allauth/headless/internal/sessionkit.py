import typing
from importlib import import_module

from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model

from allauth.headless import app_settings
from allauth.headless.constants import Client


def session_store(session_key=None):
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key=session_key)


def new_session():
    return session_store()


def expose_session_token(request):
    if request.allauth.headless.client != Client.APP:
        return
    strategy = app_settings.TOKEN_STRATEGY
    hdr_token = strategy.get_session_token(request)
    modified = request.session.modified
    empty = request.session.is_empty()
    if modified and not empty:
        new_token = strategy.create_session_token(request)
        if not hdr_token or hdr_token != new_token:
            return new_token


def authenticate_by_x_session_token(token: str) -> typing.Optional[typing.Tuple]:
    session = app_settings.TOKEN_STRATEGY.lookup_session(token)
    if not session:
        return None
    user_id_str = session.get(SESSION_KEY)
    if user_id_str:
        meta_pk = get_user_model()._meta.pk
        if meta_pk:
            user_id = meta_pk.to_python(user_id_str)
            user = get_user_model().objects.filter(pk=user_id).first()
            if user and user.is_active:
                return (user, session)
    return None
