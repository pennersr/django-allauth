import abc
import typing

from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest


class AbstractTokenStrategy(abc.ABC):
    def get_session_token(self, request: HttpRequest) -> typing.Optional[str]:
        """
        Returns the session token, if any.
        """
        token = request.headers.get("x-session-token")
        return token

    def create_access_token(self, request: HttpRequest) -> typing.Optional[str]:
        """Create an access token.

        While session tokens are required to handle the authentication process,
        depending on your requirements, a different type of token may be needed
        once authenticated.

        For example, your app likely needs access to other APIs as well. These
        APIs may even be implemented using different technologies, in which case
        having a stateless token, possibly a JWT encoding the user ID, might be
        a good fit.

        We make no assumptions in this regard. If you need access tokens, you
        will have to implement a token strategy that returns an access token
        here.
        """
        return None

    @abc.abstractmethod
    def create_session_token(self, request: HttpRequest) -> str:
        """
        Create a session token for the `request.session`.
        """
        ...

    @abc.abstractmethod
    def lookup_session(self, session_token: str) -> typing.Optional[SessionBase]:
        """
        Looks up the Django session given the session token. Returns `None`
        if the session does not / no longer exist.
        """
        ...
