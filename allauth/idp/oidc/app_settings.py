from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, TypeVar

from django.core.exceptions import ImproperlyConfigured

from allauth import app_settings as allauth_settings
from allauth.core.internal.cryptokit import UserCodeFormat


if TYPE_CHECKING:
    from allauth.idp.oidc.models import PrivateKey

_T = TypeVar("_T")


class AppSettings:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def _setting(self, name: str, dflt: _T) -> _T:
        from allauth.utils import get_setting

        return get_setting(f"{self.prefix}{name}", dflt)

    @property
    def ADAPTER(self) -> str:
        return self._setting(
            "ADAPTER",
            "allauth.idp.oidc.adapter.DefaultOIDCAdapter",
        )

    @property
    def ID_TOKEN_EXPIRES_IN(self) -> int:
        return self._setting("ID_TOKEN_EXPIRES_IN", 5 * 60)

    @property
    def PRIVATE_KEY(self) -> str:
        return self._setting("PRIVATE_KEY", "")

    @property
    def PRIVATE_KEYS(self) -> list[PrivateKey]:
        from allauth.idp.oidc.models import PrivateKey

        ret: list[PrivateKey] = []
        keys: Any = self._setting("PRIVATE_KEYS", [])
        if not isinstance(keys, (list, tuple)):
            raise ImproperlyConfigured("IDP_OIDC_PRIVATE_KEYS: must be a list")
        pem1 = self._setting("PRIVATE_KEY", "")
        seen_pems: set[str] = set()
        for key in keys:
            if not isinstance(key, dict):
                raise ImproperlyConfigured(
                    "IDP_OIDC_PRIVATE_KEYS: each entry must be a dict"
                )
            pem = key.get("pem")
            if not isinstance(pem, str):
                raise ImproperlyConfigured(
                    "IDP_OIDC_PRIVATE_KEYS: 'pem' must be a string"
                )
            if pem in seen_pems:
                raise ImproperlyConfigured("IDP_OIDC_PRIVATE_KEYS: duplicate 'pem'")
            seen_pems.add(pem)
            ret.append(
                PrivateKey(
                    pem=pem,
                    not_before=self._parse_datetime(
                        "not_before", key.get("not_before")
                    ),
                    expires_at=self._parse_datetime(
                        "expires_at", key.get("expires_at")
                    ),
                    issued_at=self._parse_datetime("issued_at", key.get("issued_at")),
                )
            )
        if pem1 and pem1 not in seen_pems:
            ret.append(PrivateKey(pem=pem1))
        return ret

    @property
    def JWKS_CACHE_CONTROL(self) -> int:
        return self._setting("JWKS_CACHE_CONTROL", 60 * 60)

    @property
    def ACCESS_TOKEN_EXPIRES_IN(self) -> int:
        return self._setting("ACCESS_TOKEN_EXPIRES_IN", 3600)

    @property
    def ACCESS_TOKEN_FORMAT(self) -> str:
        return self._setting("ACCESS_TOKEN_FORMAT", "opaque")

    @property
    def AUTH_METHODS(self) -> tuple[str, ...]:
        return tuple(
            self._setting(
                "AUTH_METHODS",
                ["client_secret_basic", "client_secret_post", "none"],
            )
        )

    @property
    def INTROSPECTION_ENABLED(self) -> bool:
        return self._setting("INTROSPECTION_ENABLED", False)

    @property
    def INTROSPECTION_AUTH_METHODS(self) -> tuple[str, ...]:
        return tuple(
            self._setting(
                "INTROSPECTION_AUTH_METHODS",
                ["client_secret_basic", "client_secret_post"],
            )
        )

    @property
    def INTROSPECTION_CROSS_CLIENT_ALLOWED(self) -> bool:
        return self._setting("INTROSPECTION_CROSS_CLIENT_ALLOWED", False)

    @property
    def AUTHORIZATION_CODE_EXPIRES_IN(self) -> int:
        return self._setting("AUTHORIZATION_CODE_EXPIRES_IN", 60)

    @property
    def ROTATE_REFRESH_TOKEN(self) -> bool:
        return self._setting("ROTATE_REFRESH_TOKEN", True)

    @property
    def REFRESH_TOKEN_EXPIRES_IN(self) -> int | None:
        return self._setting("REFRESH_TOKEN_EXPIRES_IN", None)

    @property
    def DEVICE_CODE_EXPIRES_IN(self) -> int:
        return self._setting("DEVICE_CODE_EXPIRES_IN", 300)

    @property
    def DEVICE_CODE_INTERVAL(self) -> int:
        return self._setting("DEVICE_CODE_INTERVAL", 5)

    @property
    def USER_CODE_FORMAT(self) -> UserCodeFormat:
        return self._setting("USER_CODE_FORMAT", allauth_settings.USER_CODE_FORMAT)

    @property
    def RATE_LIMITS(self) -> dict:
        rls: dict = self._setting("RATE_LIMITS", {})
        if rls is False:
            return {}
        ret = {
            # OIDC device user code checks
            "device_user_code": "5/m/ip",
            # DCR
            "client_registration": "3/m/ip",
            # CIMD fetches
            "cimd_fetch": "3/m/ip",
            # token introspection, throttled per source IP (before client
            # authentication) and per authenticated client (after).
            "introspect_ip": "30/m/ip",
            "introspect_client": "60/m/key",
        }
        ret.update(rls)
        return ret

    @property
    def RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT(self) -> bool:
        """
        At https://openid.net/specs/openid-connect-rpinitiated-1_0.html

        > 2. RP-Initiated Logout':
        > At the Logout Endpoint, the OP SHOULD ask the End-User whether to
        > log out of the OP as well.

        This setting controls whether the OP always asks.
        """
        return self._setting("RP_INITIATED_LOGOUT_ASKS_FOR_OP_LOGOUT", True)

    @property
    def USERINFO_ENDPOINT(self) -> str | None:
        """
        This setting can be used to point the ``userinfo_endpoint`` value as
        returned in the ".well-known/openid-configuration" to a custom URL.
        Setting this disables the built-in userinfo endpoint.
        """
        return self._setting("USERINFO_ENDPOINT", None)

    @property
    def DCR_ENABLED(self) -> bool:
        """
        Controls whether Dynamic Client Registration (RFC 7591) is enabled.
        """
        return self._setting("DCR_ENABLED", False)

    @property
    def DCR_REQUIRES_INITIAL_ACCESS_TOKEN(self) -> bool:
        """
        Controls whether or not an initial access token is required to
        perform Dynamic Client Registration.
        """
        return self._setting("DCR_REQUIRES_INITIAL_ACCESS_TOKEN", True)

    @property
    def CIMD_ENABLED(self) -> bool:
        """
        Whether or not CIMD is enabled.

        https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/
        https://client.dev/
        """
        return self._setting("CIMD_ENABLED", False)

    @property
    def CIMD_CACHE_TIMEOUT(self) -> int:
        """
        CIMD cache duration, in seconds.
        """
        return self._setting("CIMD_CACHE_TIMEOUT", 60 * 60)

    @staticmethod
    def _parse_datetime(field: str, value: Any) -> datetime | None:
        if value is None:
            return None
        dt: datetime | None = None
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value)
            except ValueError:
                pass
        elif isinstance(value, datetime):
            dt = value
        if dt is None:
            raise ImproperlyConfigured(
                f"IDP_OIDC_PRIVATE_KEYS: {field!r} is not a valid datetime: {value!r}"
            )
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)


_app_settings = AppSettings("IDP_OIDC_")


def __getattr__(name):
    # See https://peps.python.org/pep-0562/
    return getattr(_app_settings, name)
