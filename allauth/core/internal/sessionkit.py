from django.contrib.auth import get_user
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest


def get_session_user(session: SessionBase) -> AbstractBaseUser | None:
    request = HttpRequest()
    request.session = session
    user = get_user(request)
    if not user or user.is_anonymous:
        return None
    return user
