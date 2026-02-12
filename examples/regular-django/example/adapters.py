import base64
import json
from typing import Any, Dict, Set

from django.conf import settings

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


def get_client_id_for_provider(provider_id: str) -> str:
    """
    provider_id: e.g. 'keycloak'
    Returns the client_id from SOCIALACCOUNT_PROVIDERS['openid_connect']['APPS'].
    """
    oidc = (settings.SOCIALACCOUNT_PROVIDERS or {}).get("openid_connect", {})
    apps = oidc.get("APPS", []) or []
    for app in apps:
        if app.get("provider_id") == provider_id:
            return app["client_id"]
    raise KeyError(f"OIDC app not found for provider_id={provider_id!r}")


def _b64url_decode(segment: str) -> bytes:
    # JWT uses base64url without padding
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _decode_jwt_payload_unverified(token: str) -> Dict[str, Any]:
    """
    Decode JWT payload without verifying signature.
    This is OK for extracting claims after OIDC login, because the provider
    validation happens in the OIDC flow already.
    """
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    try:
        payload_bytes = _b64url_decode(parts[1])
        payload = json.loads(payload_bytes.decode("utf-8"))
        if isinstance(payload, dict):
            return payload
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        pass
    return {}


def _get_id_token_claims(extra_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    allauth may store id_token as a dict (decoded claims) or as a JWT string.
    Return a dict of claims either way.
    """
    id_token = (extra_data or {}).get("id_token")
    if isinstance(id_token, dict):
        return id_token
    if isinstance(id_token, str) and id_token:
        return _decode_jwt_payload_unverified(id_token)
    return {}


def extract_roles(extra_data: Dict[str, Any], provider_id: str) -> Set[str]:
    claims = _get_id_token_claims(extra_data or {})

    # 1) Realm roles: realm_access.roles
    realm_roles = set()
    realm_access = claims.get("realm_access") or {}
    if isinstance(realm_access, dict):
        rr = realm_access.get("roles") or []
        if isinstance(rr, list):
            realm_roles = {r for r in rr if isinstance(r, str)}

    # 2) Client roles: resource_access.<client_id>.roles
    client_roles = set()
    resource_access = claims.get("resource_access") or {}
    if isinstance(resource_access, dict):
        client_id = get_client_id_for_provider(provider_id)
        client_entry = resource_access.get(client_id) or {}
        if isinstance(client_entry, dict):
            cr = client_entry.get("roles") or []
            if isinstance(cr, list):
                client_roles = {r for r in cr if isinstance(r, str)}

    # Union of both
    return realm_roles | client_roles


class KeycloakRoleAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)

        # allauth stores provider claims in sociallogin.account.extra_data
        extra_data = sociallogin.account.extra_data or {}
        provider_id = sociallogin.account.provider  # e.g.: "keycloak"
        roles = sorted(extract_roles(extra_data, provider_id))

        # Store in session for fast checks
        if request is not None:
            request.session["kc_roles"] = roles

        # Keep a copy on SocialAccount (optional but handy)
        sociallogin.account.extra_data = {
            **extra_data,
            "kc_roles": roles,
        }
        sociallogin.account.save()

        return user
