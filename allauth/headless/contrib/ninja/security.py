import typing

from django.http import HttpRequest

from ninja.security.base import AuthBase

from allauth.headless.internal.sessionkit import (
    authenticate_by_x_session_token,
)


class XSessionTokenAuth(AuthBase):
    """
    This security class uses the X-Session-Token that django-allauth
    is using for authentication purposes.
    """

    openapi_type: str = "apiKey"

    def __call__(self, request: HttpRequest):
        token = self.get_session_token(request)
        if token:
            user_session = authenticate_by_x_session_token(token)
            if user_session:
                return user_session[0]
        return None

    def get_session_token(self, request: HttpRequest) -> typing.Optional[str]:
        """
        Returns the session token for the given request, by looking up the
        ``X-Session-Token`` header. Override this if you want to extract the token
        from e.g. the ``Authorization`` header.
        """
        return request.headers.get("X-Session-Token")


x_session_token_auth = XSessionTokenAuth()
