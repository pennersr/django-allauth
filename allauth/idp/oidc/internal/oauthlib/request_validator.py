import uuid
from datetime import timedelta
from typing import List, Optional

from django.utils import timezone

import jwt
from oauthlib.openid import RequestValidator

from allauth.core import context
from allauth.core.internal import jwkkit
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.clientkit import (
    is_origin_allowed,
    is_redirect_uri_allowed,
)
from allauth.idp.oidc.internal.oauthlib import authorization_codes
from allauth.idp.oidc.internal.tokens import decode_jwt_token
from allauth.idp.oidc.models import Client, Token


class OAuthLibRequestValidator(RequestValidator):

    def validate_client_id(self, client_id: str, request):
        client = self._lookup_client(request, client_id)
        if not client:
            return False
        self._use_client(request, client)
        return True

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return is_redirect_uri_allowed(
            redirect_uri,
            request.client.get_redirect_uris(),
            request.client.allow_uri_wildcards,
        )

    def validate_response_type(
        self, client_id, response_type, client, request, *args, **kwargs
    ):
        return response_type in request.client.get_response_types()

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        return set(scopes).issubset(request.client.get_scopes())

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        return request.client.get_default_scopes()

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        # WORKAROUND: docstring says:
        # > To support OIDC, you MUST associate the code with:
        # > - nonce, if present (``code["nonce"]``)
        # Yet, nonce is not there, it is in request.nonce.
        nonce = getattr(request, "nonce", None)
        if nonce:
            code = dict(**code, nonce=nonce)
        # (end WORKAROUND)
        authorization_codes.create(request.client, code, request)

    def authenticate_client_id(self, client_id, request, *args, **kwargs) -> bool:
        """Ensure client_id belong to a non-confidential client."""
        client = self._lookup_client(request, client_id)
        if not client or client.type != Client.Type.PUBLIC:
            return False
        self._use_client(request, client)
        return True

    def authenticate_client(self, request, *args, **kwargs) -> bool:
        client_id = getattr(request, "client_id", None)
        client_secret = getattr(request, "client_secret", None)
        if not isinstance(client_id, str):
            return False
        if not client_secret and request.grant_type == Client.GrantType.DEVICE_CODE:
            return self.authenticate_client_id(client_id, request)
        if not client_secret or not isinstance(client_secret, str):
            return False
        client = self._lookup_client(request, client_id)
        if not client:
            return False
        if not client.check_secret(client_secret):
            return False
        self._use_client(request, client)
        return True

    def validate_grant_type(
        self, client_id, grant_type, client, request, *args, **kwargs
    ):
        return grant_type in client.get_grant_types()

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        return authorization_codes.validate(client_id, code, request)

    def confirm_redirect_uri(
        self, client_id, code, redirect_uri, client, request, *args, **kwargs
    ) -> bool:
        authorization_code = self._lookup_authorization_code(request, client_id, code)
        if not authorization_code:
            return False
        return redirect_uri == authorization_code["redirect_uri"]

    def save_bearer_token(self, token: dict, request, *args, **kwargs):
        """
        https://datatracker.ietf.org/doc/html/rfc6749#section-6
        > The authorization server MAY issue a new refresh token, in which case
        > the client MUST discard the old refresh token and replace it with the
        > new refresh token.  The authorization server MAY revoke the old
        > refresh token after issuing a new refresh token to the client.  If a
        > new refresh token is issued, the refresh token scope MUST be
        > identical to that of the refresh token included by the client in the
        > request.

        https://datatracker.ietf.org/doc/html/rfc6749#section-1.5
        > Refresh tokens are issued to the client by the authorization server and
        > are used to obtain a new access token when the current access token becomes
        > invalid or expires, or to obtain additional access tokens with identical or
        > narrower scope
        """
        adapter = get_adapter()
        refresh_token = token.get("refresh_token")
        email = getattr(request, "email", None)
        tokens = []
        if refresh_token:
            refresh_token_hash = adapter.hash_token(refresh_token)
            rt = getattr(request, "refresh_token_instance", None)
            if rt and not email and "email" in request.scopes:
                email = rt.get_scope_email()
            if (
                rt
                and not app_settings.ROTATE_REFRESH_TOKEN
                and refresh_token_hash == rt.hash
            ):
                # We reuse our token.
                pass
            else:
                if rt:
                    # If we have an existing refresh token, drop it, because of:
                    assert (
                        app_settings.ROTATE_REFRESH_TOKEN
                        or refresh_token_hash != rt.hash
                    )  # nosec[assert_used]
                    rt.delete()
                tokens.append(
                    Token(
                        client=request.client,
                        user=request.user,
                        type=Token.Type.REFRESH_TOKEN,
                        hash=refresh_token_hash,
                    )
                )
        tokens.append(
            Token(
                client=request.client,
                user=request.user,
                type=Token.Type.ACCESS_TOKEN,
                hash=adapter.hash_token(token["access_token"]),
                expires_at=timezone.now() + timedelta(seconds=token["expires_in"]),
            )
        )
        for t in tokens:
            t.set_scopes(request.scopes)
            if email:
                t.set_scope_email(email)
        Token.objects.bulk_create(tokens)

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        authorization_codes.invalidate(client_id, code)

    def validate_user_match(self, id_token_hint, scopes, claims, request) -> bool:
        if not context.request.user:
            return False
        sub = None
        if id_token_hint:
            payload = decode_jwt_token(
                id_token_hint,
                client_id=request.client.id,
                verify_exp=True,
                verify_iss=True,
            )
            if payload is None:
                return False
            sub = payload.get("sub")
            session_sub = get_adapter().get_user_sub(
                request.client, context.request.user
            )
            if sub != session_sub:
                return False
        if claims:
            sub = claims.get("sub")
            session_sub = get_adapter().get_user_sub(
                request.client, context.request.user
            )
            if sub != session_sub:
                return False
        return True

    def get_authorization_code_scopes(
        self, client_id, code, redirect_uri, request
    ) -> List[str]:
        authorization_code = self._lookup_authorization_code(request, client_id, code)
        if not authorization_code:
            return []
        return authorization_code["scopes"]

    def get_authorization_code_nonce(self, client_id, code, redirect_uri, request):
        authorization_code = self._lookup_authorization_code(request, client_id, code)
        return authorization_code["code"].get("nonce")

    def get_code_challenge(self, code, request):
        ret = None
        authorization_code = self._lookup_authorization_code(
            request, request.client_id, code
        )
        if pkce := authorization_code.get("pkce"):
            ret = pkce["code_challenge"]
        return ret

    def get_code_challenge_method(self, code, request):
        ret = None
        authorization_code = self._lookup_authorization_code(
            request, request.client_id, code
        )
        if pkce := authorization_code.get("pkce"):
            ret = pkce["code_challenge_method"]
        return ret

    def is_pkce_required(self, client_id, request) -> bool:
        client = self._lookup_client(request, client_id)
        return bool(client and client.type == Client.Type.PUBLIC)

    def finalize_id_token(self, id_token: dict, token: dict, token_handler, request):
        """
        https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
        """
        adapter = get_adapter()
        id_token["iss"] = adapter.get_issuer()
        id_token["exp"] = id_token["iat"] + app_settings.ID_TOKEN_EXPIRES_IN
        id_token["jti"] = uuid.uuid4().hex
        email = getattr(request, "email", None)
        id_token.update(
            adapter.get_claims(
                "id_token", request.user, request.client, request.scopes, email=email
            )
        )
        adapter.populate_id_token(id_token, request.client, request.scopes)
        jwk_dict, private_key = jwkkit.load_jwk_from_pem(app_settings.PRIVATE_KEY)
        return jwt.encode(
            id_token, private_key, algorithm="RS256", headers={"kid": jwk_dict["kid"]}
        )

    def validate_bearer_token(self, token, scopes, request) -> bool:
        if not token:
            return False
        if context.request.GET.get("access_token") == token:
            # Supporting tokens in query params is considered bad practice, yet,
            # oauthlib supports this. E.g., if access tokens are sent via URI
            # query parameters, such tokens may leak to log files and the HTTP
            # 'referer'.
            return False
        instance = Token.objects.lookup(Token.Type.ACCESS_TOKEN, token)
        if not instance:
            return False
        if instance.user and not instance.user.is_active:
            return False
        granted_scopes = instance.get_scopes()
        if not set(scopes).issubset(set(granted_scopes)):
            return False
        request.user = instance.user
        self._use_client(request, instance.client)
        request.scopes = granted_scopes
        request.access_token = instance
        return True

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        if token_type_hint == "access_token":  # nosec
            types = [Token.Type.ACCESS_TOKEN]
        elif token_type_hint == "refresh_token":  # nosec
            types = [Token.Type.REFRESH_TOKEN]
        else:
            types = [Token.Type.ACCESS_TOKEN, Token.Type.REFRESH_TOKEN]
        Token.objects.by_value(token).filter(type__in=types).delete()

    def get_userinfo_claims(self, request):
        email = request.access_token.get_scope_email()
        return get_adapter().get_claims(
            "userinfo", request.user, request.client, request.scopes, email=email
        )

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        # https://openid.net/specs/openid-financial-api-part-1-1_0.html#section-5.2.2
        # 9. shall require the redirect_uri in the authorization request;
        # So, don't support a default.
        return None

    def validate_user(self, username, password, client, request, *args, **kwargs):
        """
        Note that this bypasses MFA, which is why the password grant is not
        recommended and hence disabled. This could work:

            try:
                user = get_account_adapter().authenticate(
                    context.request, username=username, password=password
                )
            except ValidationError:
                return False
            else:
                if not user:
                    return False
                request.user = user
                return True
        """
        return False

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        token = Token.objects.filter(client=client).lookup(
            Token.Type.REFRESH_TOKEN, refresh_token
        )
        if not token:
            return False
        if not token.user or not token.user.is_active:
            return False
        request.user = token.user
        request.refresh_token_instance = token
        return True

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        return request.refresh_token_instance.get_scopes()

    def client_authentication_required(self, request, *args, **kwargs) -> bool:
        if request.client_id and request.client_secret:
            return True

        client = self._lookup_client(request, request.client_id)
        if client and client.type == Client.Type.PUBLIC:
            return False
        return super().client_authentication_required(request, *args, **kwargs)

    def _lookup_client(self, request, client_id) -> Optional[Client]:
        """
        In various places, oauthlib documents:

            Note, while not strictly necessary it can often be very convenient
            to set request.client to the client object associated with the
            given client_id.

        It's unclear though that if this is not explicitly stated, and, we still
        were to set request.client, whether that could have adverse side
        effects. So, don't assign request.client here.
        """
        cache = request._client_cache = getattr(request, "_client_cache", {})
        if client_id in cache:
            client = cache[client_id]
        else:
            client = Client.objects.filter(id=client_id).first()
            cache[client_id] = client
        return client

    def _use_client(self, request, client: Client) -> None:
        request.client = client
        request.client.client_id = client.id  # type:ignore[attr-defined]

    def _lookup_authorization_code(
        self, request, client_id: str, code: str
    ) -> Optional[dict]:
        cache = request._code_cache = getattr(request, "_code_cache", {})
        key = (client_id, code)
        if key in cache:
            authorization_code = cache[key]
        else:
            authorization_code = authorization_codes.lookup(client_id, code)
            cache[key] = authorization_code
        return authorization_code

    def is_origin_allowed(self, client_id, origin, request, *args, **kwargs) -> bool:
        client = self._lookup_client(request, client_id)
        return bool(
            client
            and is_origin_allowed(
                origin, client.get_cors_origins(), client.allow_uri_wildcards
            )
        )

    def rotate_refresh_token(self, request):
        return app_settings.ROTATE_REFRESH_TOKEN

    def validate_silent_login(self, request) -> bool:
        if context.request.user.is_authenticated:
            request.user = context.request.user
            return True
        return False

    def validate_silent_authorization(self, request) -> bool:
        granted_scopes = set()
        tokens = Token.objects.valid().filter(
            user=context.request.user,
            type__in=[Token.Type.REFRESH_TOKEN, Token.Type.ACCESS_TOKEN],
        )
        for token in tokens.iterator():
            granted_scopes.update(token.get_scopes())
        return set(request.scopes).issubset(granted_scopes)

    def validate_jwt_bearer_token(self, token, scopes, request):
        if scopes:
            # We don't have scope for the ID token
            return False
        payload = decode_jwt_token(token, verify_iss=True, verify_exp=True)
        if payload is None:
            return False
        return self.validate_client_id(payload["aud"], request)
