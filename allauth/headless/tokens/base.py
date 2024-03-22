import abc


class AbstractTokenStrategy(abc.ABC):
    def get_access_token(self, request):
        hdr = request.headers.get("authorization")
        if not hdr:
            return None
        parts = hdr.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]

    def get_session_token(self, request):
        token = request.headers.get("x-session-token")
        return token

    @abc.abstractmethod
    def create_access_token(self, request):
        return None

    @abc.abstractmethod
    def create_session_token(self, request):
        ...

    @abc.abstractmethod
    def lookup_session(self, session_token):
        ...
