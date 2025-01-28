from django.http import HttpRequest

from ninja.security.base import AuthBase

from allauth.headless.internal.sessionkit import (
    authenticate_by_x_session_token,
)


class XSessionTokenAuth(AuthBase):
    openapi_type: str = "apiKey"

    def __call__(self, request: HttpRequest):
        token = request.headers.get("X-Session-Token")
        if token:
            user_session = authenticate_by_x_session_token(token)
            if user_session:
                return user_session[0]
        return None


x_session_token_auth = XSessionTokenAuth()
