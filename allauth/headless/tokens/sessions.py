from allauth.headless.internal import sessionkit
from allauth.headless.tokens.base import AbstractTokenStrategy


class SessionTokenStrategy(AbstractTokenStrategy):
    def create_access_token(self, request):
        return f"at-{request.session.session_key}"

    def create_session_token(self, request):
        if not request.session.session_key:
            request.session.save()
        return f"st-{request.session.session_key}"

    def is_access_token_valid(self, request, access_token):
        return False

    def lookup_session(self, session_token):
        if len(session_token) > 3 and session_token.startswith("st-"):
            session_key = session_token[3:]
            if sessionkit.session_store().exists(session_key):
                return sessionkit.session_store(session_key)
