from __future__ import annotations

import hashlib
import uuid
import warnings
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Literal
from urllib.parse import urlsplit

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from django.utils import timezone
from django.utils.functional import Promise
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from allauth.account.internal.userkit import (
    str_to_user_id,
    user_id_to_str,
    user_username,
)
from allauth.account.models import EmailAddress
from allauth.core.internal.adapter import BaseAdapter
from allauth.core.internal.cryptokit import generate_user_code
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.internal.private_keys import filter_keys, pick_signing_key


if TYPE_CHECKING:
    from allauth.idp.oidc.models import Client, PrivateKey, Token


class DefaultOIDCAdapter(BaseAdapter):
    """The adapter class allows you to override various functionality of the
    ``allauth.idp.oidc`` app.  To do so, point ``settings.IDP_OIDC_ADAPTER`` to
    your own class that derives from ``DefaultOIDCAdapter`` and override the
    behavior by altering the implementation of the methods according to your own
    needs.
    """

    # Deprecated. Populate settings.IDP_OIDC_SCOPE_CHOICES instead.
    scope_display: ClassVar[dict[str, str | Promise]] = {
        "openid": _("View your user ID"),
        "email": _("View your email address"),
        "profile": _("View your basic profile information"),
    }

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "scope_display" in cls.__dict__:
            warnings.warn(
                "Overriding DefaultOIDCAdapter.scope_display is deprecated; use "
                "IDP_OIDC_SCOPE_CHOICES or override get_scope_choices().",
                DeprecationWarning,
                stacklevel=2,
            )

    def generate_client_id(self) -> str:
        """
        The client ID to use for newly created clients.
        """
        return uuid.uuid4().hex

    def generate_client_secret(self) -> str:
        """
        The client secret to use for newly created clients.
        """
        return get_random_secret_key()

    def generate_user_code(self) -> str:
        return generate_user_code(**app_settings.USER_CODE_FORMAT)

    def hash_token(self, token: str) -> str:
        """
        We don't store tokens directly, only the hash of the token. This methods generates
        that hash.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def get_issuer(self) -> str:
        """
        Returns the URL of the issuer.
        """
        return self.request.build_absolute_uri("/").rstrip("/")

    def populate_id_token(
        self,
        id_token: dict[str, Any],
        client: Client,
        scopes: Iterable[str],
        **kwargs: Any,
    ) -> None:
        """
        This method can be used to alter the ID token payload. It is already populated
        with basic values. Depending on the client and requested scopes, you can
        expose additional information here.
        """
        pass

    def populate_access_token(
        self,
        access_token: dict[str, Any],
        *,
        client: Client,
        scopes: Iterable[str],
        user: AbstractBaseUser,
        **kwargs: Any,
    ) -> None:
        """
        This method can be used to alter the JWT access token payload. It is already
        populated with basic values.
        """
        pass

    def get_claims(
        self,
        purpose: Literal["id_token", "userinfo"],
        user: AbstractBaseUser,
        client: Client,
        scopes: Iterable[str],
        email: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Return the claims to be included in the ID token or userinfo response.
        """
        claims: dict[str, Any] = {"sub": self.get_user_sub(client, user)}
        if "email" in scopes:
            address: EmailAddress | None = None
            if email:
                try:
                    address = EmailAddress.objects.get_for_user(user, email)
                except EmailAddress.DoesNotExist:
                    pass
            else:
                address = EmailAddress.objects.get_primary(user)
            if address:
                claims.update(
                    {
                        "email": address.email,
                        "email_verified": address.verified,
                    }
                )
        if "profile" in scopes:
            if hasattr(user, "get_full_name"):
                full_name = user.get_full_name()
            else:
                full_name = ""
            last_name = getattr(user, "last_name", None)
            first_name = getattr(user, "first_name", None)
            username = user_username(user)
            profile_claims = {
                "name": full_name,
                "given_name": first_name,
                "family_name": last_name,
                "preferred_username": username,
            }
            for claim_key, claim_value in profile_claims.items():
                if claim_value:
                    claims[claim_key] = claim_value
        return claims

    def get_user_sub(self, client: Client, user: AbstractBaseUser) -> str:
        """
        Returns the "sub" (subject identifier) for the given user.
        """
        return user_id_to_str(user)

    def get_user_by_sub(self, client: Client, sub: str) -> AbstractBaseUser | None:
        """
        Looks up a user, given its subject identifier. Returns `None` if no
        such user was found.
        """
        try:
            pk = str_to_user_id(sub)
        except ValueError:
            return None
        user = get_user_model().objects.filter(pk=pk).first()
        if not user or not user.is_active:
            return None
        return user

    def validate_client_registration(
        self,
        *,
        client: Client,
        client_metadata: dict[str, Any],
        token: Token | None,
        bearer_token: str | None,
        **kwargs: Any,
    ) -> None:
        """
        This method is called after all builtin validation was successful,
        and just before the actual client is being created. To intervene, raise
        a ``ValidationError`` or an ``ImmediateHttpResponse``.

        ``client``: The ``Client`` instance that is about to be saved.
        ``client_metadata``: The raw JSON payload from the DCR request.
        ``token``: The ``Token`` instance corresponding to the initial access
            token, or ``None`` if no token was provided.
        ``bearer_token``: The raw bearer token string from the ``Authorization``
            header, or ``None`` if no token was provided.
        """
        pass

    def validate_resource_uris(self, *, uris: list[str], **kwargs: Any) -> None:
        """
        Allows for custom validation of resource URIs (RFC 8707).
        Throw a ``ValidationError`` to reject the resource.
        """
        pass

    def populate_server_metadata(self, data: dict[str, str | list[str]]) -> None:
        """
        Allows for customizing the ``/.well-known/openid-configuration``
        payload, as specified in `RFC 8414`_ (OAuth 2.0 Authorization Server
        Metadata).

        .. _RFC 8414: https://www.rfc-editor.org/info/rfc8414
        """
        pass

    def is_cimd_url_allowed(self, url: str) -> bool:
        """
        Determines whether the given CIMD (Client ID Metadata Document) URL is
        accepted as a ``client_id``. The default implementation checks
        the host name against ``IDP_OIDC_CIMD_ALLOWED_HOSTS``.
        """
        allowed_hosts = app_settings.CIMD_ALLOWED_HOSTS
        return "*" in allowed_hosts or urlsplit(url).hostname in allowed_hosts

    def get_jwks_cache_control(self) -> int:
        """
        Returns the cache control value for the JWKS endpoint. The default
        implementation returns the value of the ``IDP_OIDC_JWKS_CACHE_CONTROL``
        setting, clamped so that clients refetch before the next key drops out
        of the key set (i.e. before the soonest ``expires_at``).  Override this
        method to provide a different cache control value, e.g. in case of a
        secret manager / vault is used.
        """
        cache_control = app_settings.JWKS_CACHE_CONTROL
        now = timezone.now()
        # Clamp against the same key set that is actually published (so a custom
        # ``list_private_keys()`` override cannot diverge from the cache window).
        for key in self.list_private_keys(is_active=True):
            if key.expires_at is not None:
                cache_control = min(
                    cache_control, int((key.expires_at - now).total_seconds())
                )
        return max(0, cache_control)

    def list_private_keys(
        self,
        *,
        did_activate: Literal[True] | None = None,
        is_active: Literal[True] | None = None,
    ) -> list[PrivateKey]:
        """
        Returns the configured private keys, optionally filtered.  Pass
        ``did_activate=True`` to exclude keys whose ``not_before`` lies in the
        future, and/or ``is_active=True`` to exclude keys past their
        ``expires_at``.  Used both for token verification and for serving
        ``.well-known/jwks.json``.
        """
        return filter_keys(
            app_settings.PRIVATE_KEYS, did_activate=did_activate, is_active=is_active
        )

    def get_signing_key(self) -> PrivateKey:
        """
        Returns the private key used for signing new tokens: the most recently
        issued key that has activated and not yet expired.  Raises
        ``ImproperlyConfigured`` if no such key is found.
        """
        key = pick_signing_key(
            self.list_private_keys(did_activate=True, is_active=True)
        )
        if key is None:
            raise ImproperlyConfigured("No active private key.")
        return key

    def populate_introspection_response(
        self, *, response: dict[str, Any], token: Token
    ) -> None:
        """
        This method can be used to add additional information to the introspection
        response for a given token. The default implementation does nothing.
        """
        return None

    def is_introspection_allowed(
        self,
        token: Token,
        *,
        caller_client: Client,
    ) -> bool:
        """
        This method can be used to add additional checks to determine if a token is
        valid in introspection responses and if the caller client is allowed to introspect it.
        The default implementation allows all introspection requests for active tokens,
        regardless of the caller client.

        ``caller_client``: The authenticated introspection caller client.
        """
        return True

    def get_scope_choices(self) -> list[tuple[str, str | Promise]]:
        """
        Returns all supported scopes and their display labels
        """
        choices: list[tuple[str, str | Promise]] = []
        for scope, display in app_settings.SCOPE_CHOICES:
            if scope == display:
                # For backwards compatibility only.
                display = self.scope_display.get(scope, scope)
            choices.append((scope, display))
        return choices

    def get_default_scopes(self, *, client: Client, **kwargs: Any) -> list[str]:
        """
        The scopes used during authorization when no ``scope`` parameter is
        explicitly passed.
        """
        return client.get_default_scopes() or app_settings.DEFAULT_SCOPES

    def get_cimd_default_scopes(
        self,
        *,
        client: Client,
        client_metadata: dict[str, Any],
        **kwargs: Any,
    ) -> list[str]:
        """
        The scopes assigned when a Client ID Metadata Document omits the
        ``scope`` metadata field.

        ``client`` is the client instance that is about to be created dynamically.
        ``client_metadata`` contains the fetched Client ID Metadata Document.
        """
        return app_settings.CIMD_DEFAULT_SCOPES

    def get_dcr_default_scopes(self, *, client: Client, **kwargs: Any) -> list[str]:
        """
        The scopes assigned during dynamic client registration when the client
        omits the ``scope`` metadata field.
        """
        return app_settings.DCR_DEFAULT_SCOPES


def get_adapter() -> DefaultOIDCAdapter:
    return import_string(app_settings.ADAPTER)()
