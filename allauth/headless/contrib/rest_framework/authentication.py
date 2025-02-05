import typing

from django.http import HttpRequest

from rest_framework import authentication

from allauth.headless.internal.sessionkit import (
    authenticate_by_x_session_token,
)


class XSessionTokenAuthentication(authentication.BaseAuthentication):
    """
    This authentication class uses the X-Session-Token that django-allauth
    is using for authentication purposes.
    """

    def authenticate(self, request: HttpRequest):
        token = self.get_session_token(request)
        if token:
            return authenticate_by_x_session_token(token)
        return None

    def get_session_token(self, request: HttpRequest) -> typing.Optional[str]:
        """
        Returns the session token for the given request, by looking up the
        ``X-Session-Token`` header. Override this if you want to extract the token
        from e.g. the ``Authorization`` header.
        """
        return request.headers.get("X-Session-Token")
