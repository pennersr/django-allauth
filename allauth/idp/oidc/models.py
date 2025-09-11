from typing import List, Optional

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.clientkit import _validate_uri_wildcard_format


def default_client_id() -> str:
    adapter = get_adapter()
    client_id = adapter.generate_client_id()
    return client_id


def default_client_secret() -> str:
    adapter = get_adapter()
    client_secret = adapter.generate_client_secret()
    return make_password(client_secret)


def _values_from_text(text) -> List[str]:
    return list(filter(None, [s.strip() for s in text.split("\n")]))


def _values_to_text(values) -> str:
    if isinstance(values, str):
        raise ValueError(values)
    return "\n".join(values)


class Client(models.Model):
    class GrantType(models.TextChoices):
        AUTHORIZATION_CODE = "authorization_code", _("Authorization code")
        DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code", _("Device code")
        CLIENT_CREDENTIALS = "client_credentials", _("Client credentials")
        REFRESH_TOKEN = "refresh_token", _("Refresh token")

    class Type(models.TextChoices):
        CONFIDENTIAL = "confidential", _("Confidential")
        PUBLIC = "public", _("Public")

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

    def get_redirect_uris(self) -> List[str]:
        return _values_from_text(self.redirect_uris)

    def set_redirect_uris(self, uris: List[str]):
        self.redirect_uris = _values_to_text(uris)

    def get_cors_origins(self) -> List[str]:
        return _values_from_text(self.cors_origins)

    def set_cors_origins(self, uris: List[str]):
        self.cors_origins = _values_to_text(uris)

    def get_scopes(self) -> List[str]:
        return _values_from_text(self.scopes)

    def set_scopes(self, scopes: List[str]) -> None:
        self.scopes = _values_to_text(scopes)

    def get_default_scopes(self) -> List[str]:
        return _values_from_text(self.default_scopes)

    def set_default_scopes(self, scopes: List[str]) -> None:
        self.default_scopes = _values_to_text(scopes)

    def get_response_types(self) -> List[str]:
        return _values_from_text(self.response_types)

    def set_response_types(self, response_types: List[str]) -> None:
        self.response_types = _values_to_text(response_types)

    def get_grant_types(self) -> List[str]:
        return _values_from_text(self.grant_types)

    def set_grant_types(self, grant_types: List[str]):
        self.grant_types = _values_to_text(grant_types)

    def set_secret(self, secret) -> None:
        self.secret = make_password(secret)

    def check_secret(self, secret: str) -> bool:
        return check_password(secret, self.secret)

    def clean_redirect_uris(self):
        uris = self.get_redirect_uris()
        for uri in uris:
            _validate_uri_wildcard_format(uri, self.allow_uri_wildcards)
        return uris

    def clean_cors_origins(self):
        origins = self.get_cors_origins()
        for origin in origins:
            _validate_uri_wildcard_format(origin, self.allow_uri_wildcards)
        return origins

    def clean(self):
        # the django admin doesn't call full_clean, so we need to call them here
        self.clean_redirect_uris()
        self.clean_cors_origins()

    def __str__(self) -> str:
        return self.id


class TokenQuerySet(models.query.QuerySet):
    def valid(self):
        return self.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )

    def by_value(self, value: str):
        return self.filter(hash=get_adapter().hash_token(value))

    def lookup(self, type, value):
        return self.valid().by_value(value).filter(type=type).first()


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

    def get_scopes(self) -> List[str]:
        return _values_from_text(self.scopes)

    def set_scopes(self, scopes: List[str]) -> None:
        self.scopes = _values_to_text(scopes)

    def set_scope_email(self, email: str) -> None:
        """
        In case a specific email was chosen to be exposed to the client,
        store that using this method.
        """
        if self.data is None:
            self.data = {}
        self.data["email"] = email

    def get_scope_email(self) -> Optional[str]:
        """
        Returns the email that was selected when the email scope was
        granted.  Note that this may e outdated, as the user can change email
        addresses at any time.
        """
        if not isinstance(self.data, dict):
            return None
        return self.data.get("email")
