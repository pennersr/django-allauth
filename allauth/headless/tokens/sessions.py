import typing

from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest

from allauth.headless.internal import sessionkit
from allauth.headless.tokens.base import AbstractTokenStrategy


class SessionTokenStrategy(AbstractTokenStrategy):
    def create_session_token(self, request: HttpRequest) -> str:
        if not request.session.session_key:
            request.session.save()
        key = request.session.session_key
        assert isinstance(key, str)  # We did save.
        return key

    def lookup_session(self, session_token: str) -> typing.Optional[SessionBase]:
        session_key = session_token
        if sessionkit.session_store().exists(session_key):
            return sessionkit.session_store(session_key)
        return None
