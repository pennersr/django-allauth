from __future__ import annotations

import logging
from collections.abc import Collection, Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allauth.idp.oidc.adapter import get_adapter


logger = logging.getLogger(__name__)


def default_client_id() -> str:
    adapter = get_adapter()
    client_id = adapter.generate_client_id()
    return client_id


def default_client_secret() -> str:
    adapter = get_adapter()
    client_secret = adapter.generate_client_secret()
    return make_password(client_secret)


def _values_from_text(text: str) -> list[str]:
    return list(filter(None, [s.strip() for s in text.split("\n")]))


def _values_to_text(values: list[str]) -> str:
    if isinstance(values, str):
        raise ValueError(values)
    return "\n".join(values)


class Client(models.Model):
    class GrantType(models.TextChoices):
        AUTHORIZATION_CODE = "authorization_code", _("Authorization code")
        DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code", _("Device code")
        CLIENT_CREDENTIALS = "client_credentials", _("Client credentials")
        REFRESH_TOKEN = "refresh_token", _("Refresh token")

    class ResponseType(models.TextChoices):
        CODE = "code", _("Code")
        TOKEN = "token", _("Token")
        ID_TOKEN = "id_token", _("ID token")
        ID_TOKEN_TOKEN = "id_token token", _("ID token token")
        CODE_TOKEN = "code token", _("Code token")
        CODE_ID_TOKEN = "code id_token", _("Code ID token")
        CODE_ID_TOKEN_TOKEN = "code id_token token", _("Code ID token token")
        NONE = "none", _("None")

    class Type(models.TextChoices):
        CONFIDENTIAL = "confidential", _("Confidential")
        PUBLIC = "public", _("Public")

    class AuthenticationMethod(models.TextChoices):
        # token_endpoint_auth_method values this server supports (the IANA
        # registry is open-ended; only add a value once the token endpoint
        # actually honors it).
        NONE = "none", _("None")
        CLIENT_SECRET_BASIC = "client_secret_basic", _("Client secret basic")
        CLIENT_SECRET_POST = "client_secret_post", _("Client secret post")

    id = models.CharField(
        primary_key=True,
        max_length=100,
        default=default_client_id,
        verbose_name="Client ID",
    )
    name = models.CharField(
        max_length=100,
    )
    secret = models.CharField(max_length=200, default=default_client_secret)
    scopes = models.TextField(
        help_text=_(
            "The scope(s) the client is allowed to request. Provide one value per line, e.g.: openid(ENTER)profile(ENTER)email(ENTER)"
        ),
        default="openid",
    )
    default_scopes = models.TextField(
        help_text=_(
            "In case the client does not specify any scope, these default scopes are used. Provide one value per line, e.g.: openid(ENTER)profile(ENTER)email(ENTER)"
        ),
        default="",
        blank=True,
    )
    type = models.CharField(
        max_length=20, default=Type.CONFIDENTIAL, choices=Type.choices
    )
    grant_types = models.TextField(
        default=GrantType.AUTHORIZATION_CODE,
        help_text=_(
            "A list of allowed grant types. Provide one value per line, e.g.: authorization_code(ENTER)client_credentials(ENTER)refresh_token(ENTER)"
        ),
    )
    redirect_uris = models.TextField(
        help_text="A list of allowed redirect (callback) URLs, one per line.",
        blank=True,
        default="",
    )
    cors_origins = models.TextField(
        blank=True,
        help_text=_(
            "A list of allowed origins for cross-origin requests, one per line."
        ),
        default="",
        verbose_name="CORS allowed origins",
    )
    allow_uri_wildcards = models.BooleanField(
        default=False,
        help_text=_(
            "Allow wildcards (*) in redirect URIs and CORS origins. "
            "When enabled, URIs can contain a single asterisk to match subdomains."
        ),
        verbose_name="Allow URI wildcards",
    )
    response_types = models.TextField(
        default="code",
        help_text=_(
            "A list of allowed response types. Provide one value per line, e.g.: code(ENTER)id_token token(ENTER)"
        ),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE
    )
    skip_consent = models.BooleanField(
        default=False, help_text="Flag to allow skip the consent screen for this client"
    )
    created_at = models.DateTimeField(default=timezone.now)
    data = models.JSONField(blank=True, null=True, default=None)

    class Meta:
        verbose_name = _("client")
        verbose_name_plural = _("clients")

    def get_redirect_uris(self) -> list[str]:
        return _values_from_text(self.redirect_uris)

    def set_redirect_uris(self, uris: list[str]) -> None:
        self.redirect_uris = _values_to_text(uris)

    def set_post_logout_redirect_uris(self, uris: list[str]) -> None:
        metadata = self._get_client_metadata()
        if metadata is None:
            if self.data is None:
                self.data = {}
            metadata = self.data["client_metadata"] = {}
        metadata["post_logout_redirect_uris"] = uris

    def get_post_logout_redirect_uris(self) -> list[str]:
        dflt: list[str] = []
        metadata = self._get_client_metadata()
        if not metadata:
            return dflt
        uris = metadata.get("post_logout_redirect_uris")
        if uris is None:
            return dflt
        if not isinstance(uris, list) or not all(isinstance(uri, str) for uri in uris):
            logger.warning("Client %s has malformed post_logout_redirect_uris", self.pk)
            return dflt
        return uris

    def _get_client_metadata(self) -> dict[str, Any] | None:
        if self.data is None:
            return None
        if not isinstance(self.data, dict):
            logger.warning("Client %s has non-dict data", self.pk)
            return None
        metadata = self.data.get("client_metadata")
        if metadata is not None and not isinstance(metadata, dict):
            logger.warning("Client %s has non-dict client_metadata", self.pk)
            return None
        return metadata

    def get_cors_origins(self) -> list[str]:
        return _values_from_text(self.cors_origins)

    def set_cors_origins(self, uris: list[str]) -> None:
        self.cors_origins = _values_to_text(uris)

    def get_scopes(self) -> list[str]:
        return _values_from_text(self.scopes)

    def set_scopes(self, scopes: list[str]) -> None:
        self.scopes = _values_to_text(scopes)

    def get_default_scopes(self) -> list[str]:
        return _values_from_text(self.default_scopes)

    def set_default_scopes(self, scopes: list[str]) -> None:
        self.default_scopes = _values_to_text(scopes)

    def get_response_types(self) -> list[str]:
        return _values_from_text(self.response_types)

    def set_response_types(self, response_types: list[str]) -> None:
        self.response_types = _values_to_text(response_types)

    def get_grant_types(self) -> list[str]:
        return _values_from_text(self.grant_types)

    def set_grant_types(self, grant_types: list[str]) -> None:
        self.grant_types = _values_to_text(grant_types)

    def set_secret(self, secret: str) -> None:
        self.secret = make_password(secret)

    def check_secret(self, secret: str) -> bool:
        return check_password(secret, self.secret)

    def clean_redirect_uris(self) -> list[str]:
        from allauth.idp.oidc.internal.clientkit import _validate_uri_wildcard_format

        uris = self.get_redirect_uris()
        for uri in uris:
            _validate_uri_wildcard_format(uri, self.allow_uri_wildcards)
        return uris

    def clean_cors_origins(self) -> list[str]:
        from allauth.idp.oidc.internal.clientkit import _validate_uri_wildcard_format

        origins = self.get_cors_origins()
        for origin in origins:
            _validate_uri_wildcard_format(origin, self.allow_uri_wildcards)
        return origins

    def clean(self) -> None:
        # the django admin doesn't call full_clean, so we need to call them here
        self.clean_redirect_uris()
        self.clean_cors_origins()

    def __str__(self) -> str:
        return self.id


class TokenQuerySet(models.query.QuerySet["Token"]):
    def valid(self) -> TokenQuerySet:
        return self.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

    def expired(self) -> TokenQuerySet:
        return self.filter(expires_at__isnull=False, expires_at__lte=timezone.now())

    def by_value(self, value: str) -> TokenQuerySet:
        return self.filter(hash=get_adapter().hash_token(value))

    def lookup(self, type, value: str) -> Token | None:
        return self.valid().by_value(value).filter(type=type).first()

    def lookup_by_value(
        self, types: Collection[Token.Type], value: str
    ) -> Token | None:
        try:
            return self.valid().by_value(value).get(type__in=types)
        except (Token.DoesNotExist, Token.MultipleObjectsReturned):
            return None


class Token(models.Model):
    objects = TokenQuerySet.as_manager()

    class Type(models.TextChoices):
        INITIAL_ACCESS_TOKEN = "ia", "Initial access token"
        ACCESS_TOKEN = "at", "Access token"
        REFRESH_TOKEN = "rt", "Refresh token"
        AUTHORIZATION_CODE = "ac", "Authorization code"

    type = models.CharField(max_length=2, choices=Type.choices)
    hash = models.CharField(max_length=255)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    data = models.JSONField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True, db_index=True)
    scopes = models.TextField(default="")

    class Meta:
        unique_together = (("type", "hash"),)

    def __str__(self) -> str:
        if self.user_id:
            return f"{self.get_type_display()} for user #{self.user_id}"
        return self.get_type_display()

    def set_value(self, value: str) -> None:
        self.hash = get_adapter().hash_token(value)

    def get_scopes(self) -> list[str]:
        return _values_from_text(self.scopes)

    def set_scopes(self, scopes: list[str]) -> None:
        self.scopes = _values_to_text(scopes)

    def set_scope_email(self, email: str) -> None:
        """
        In case a specific email was chosen to be exposed to the client,
        store that using this method.
        """
        self._data_set("email", email)

    def get_scope_email(self) -> str | None:
        """
        Returns the email that was selected when the email scope was
        granted.  Note that this may e outdated, as the user can change email
        addresses at any time.
        """
        return self._data_get("email")

    def get_grant_id(self) -> str | None:
        grant_id = self._data_get("grant_id")
        return grant_id if isinstance(grant_id, str) else None

    def set_grant_id(self, grant_id: str) -> None:
        self._data_set("grant_id", grant_id)

    def get_redirect_uri(self) -> str | None:
        redirect_uri = self._data_get("redirect_uri")
        return redirect_uri if isinstance(redirect_uri, str) else None

    def set_redirect_uri(self, redirect_uri: str) -> None:
        self._data_set("redirect_uri", redirect_uri)

    def get_nonce(self) -> str | None:
        nonce = self._data_get("nonce")
        return nonce if isinstance(nonce, str) else None

    def set_nonce(self, nonce: str) -> None:
        self._data_set("nonce", nonce)

    def get_resources(self) -> list[str]:
        resources = self._data_get("resources", [])
        if not isinstance(resources, list) or not all(
            isinstance(res, str) for res in resources
        ):
            return []
        return resources

    def set_resources(self, resources: Iterable[str]) -> None:
        self._data_set("resources", list(resources))

    def _data_get(self, key: str, dflt: Any = None) -> Any:
        if not isinstance(self.data, dict):
            return dflt
        return self.data.get(key, dflt)

    def _data_set(self, key: str, value: Any) -> None:
        if self.data is None:
            self.data = {}
        if not isinstance(self.data, dict):
            raise ValueError
        self.data[key] = value


@dataclass(frozen=True, kw_only=True)
class PrivateKey:
    not_before: datetime | None = None
    expires_at: datetime | None = None
    issued_at: datetime | None = None
    pem: str
