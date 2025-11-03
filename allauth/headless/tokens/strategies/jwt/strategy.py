from typing import Any, Dict, Optional, Tuple

from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest

from allauth.core.internal.httpkit import get_authorization_credential
from allauth.headless import app_settings
from allauth.headless.internal import sessionkit
from allauth.headless.tokens.strategies.base import AbstractTokenStrategy
from allauth.headless.tokens.strategies.jwt import internal


class JWTTokenStrategy(AbstractTokenStrategy):
    def get_session_token(self, request: HttpRequest) -> Optional[str]:
        ret = super().get_session_token(request)
        if ret:
            return ret
        payload = self._get_access_token(request)
        if not payload:
            return None
        return internal.session_key_from_sid(payload["sid"])

    def _get_access_token(self, request: HttpRequest):
        access_token = get_authorization_credential(
            request, app_settings.JWT_AUTHORIZATION_HEADER_SCHEME
        )
        if access_token is None:
            return None
        user_payload = internal.validate_access_token(access_token)
        if user_payload is None:
            return None
        return user_payload[1]

    def create_session_token(self, request: HttpRequest) -> str:
        assert request.user.is_authenticated  # nosec
        if not request.session.session_key:
            request.session.save()
        key = request.session.session_key
        # We did save
        assert isinstance(key, str)  # nosec
        return key

    def create_access_token_payload(
        self, request: HttpRequest
    ) -> Optional[Dict[str, Any]]:
        ret = super().create_access_token_payload(request)
        if ret is not None:
            ret["refresh_token"] = internal.create_refresh_token(
                request.user, request.session
            )
        return ret

    def lookup_session(self, session_token: str) -> Optional[SessionBase]:
        return sessionkit.lookup_session(session_token)

    def create_access_token(self, request: HttpRequest) -> Optional[str]:
        claims = self.get_claims(request.user)
        return internal.create_access_token(request.user, request.session, claims)

    def get_claims(self, user) -> Dict[str, Any]:
        """
        Returns additional claims to be included in the access token.  Note that
        the following claims are reserved and will be automatically set by allauth regardless of what you return:
         - ``iat``
         - ``exp``
         - ``sid``
         - ``jti``
         - ``token_use``
         - ``sub``
        """
        return {}

    def refresh_token(self, refresh_token: str) -> Optional[Tuple[str, str]]:
        user_session_payload = internal.validate_refresh_token(refresh_token)
        if user_session_payload is None:
            return None
        user, session, payload = user_session_payload
        access_token = internal.create_access_token(
            user, session, self.get_claims(user)
        )
        if app_settings.JWT_ROTATE_REFRESH_TOKEN:
            internal.invalidate_refresh_token(session, payload)
            next_refresh_token = internal.create_refresh_token(user, session)
        else:
            next_refresh_token = refresh_token
        session.save()
        return access_token, next_refresh_token
