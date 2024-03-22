from allauth.headless.internal import sessionkit


class AbstractTokenStrategy:
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
                return sessionkit.session_store(session_key), True
        return None, False
