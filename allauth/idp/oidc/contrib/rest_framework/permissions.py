from typing import Union

from rest_framework.permissions import BasePermission

from allauth.idp.oidc.internal.scope import is_scope_granted
from allauth.idp.oidc.models import Token


class TokenPermission(BasePermission):
    scope = None

    def has_permission(self, request, view) -> bool:
        access_token = request.auth
        if (
            not isinstance(access_token, Token)
            or access_token.type != Token.Type.ACCESS_TOKEN
        ):
            return False
        return is_scope_granted(self.scope, access_token, request.method)

    @classmethod
    def has_scope(cls, scope: Union[str, list, dict]):
        """
        Constructs and returns specific permission **class** (not instance)
        that checks that the request is authenticated by means of a token (see:
        ``TokenAuthentication``), and, that this token has the specified
        ``scope`` granted.

        The scope passed can either be:

        - a single scope (``str``),
        - a list of scopes, all of which should be granted.
        - a list of scope lists. Your token should match at least all scopes of one of the scope lists.
        - A dictionary, with the request method (e.g. ``GET``) as key, and one
          of the scope values from the previous bullet. The scopes to match are
          then dynamically selected based on the request.

        """

        class TokenHasScopePermission(cls):  # type: ignore[valid-type,misc]
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.scope = scope

        return TokenHasScopePermission
