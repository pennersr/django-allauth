from typing import Optional

from django.core.cache import cache

from allauth.account.models import EmailAddress
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Client


def cache_key(client_id: str, code: str) -> str:
    return f"allauth.idp.oidc.authorization_code[{client_id}:{code}]"


def create(client: Client, code: dict, request) -> None:
    adapter = get_adapter()
    authorization_code = {
        "code": code,
        "client_id": client.id,
        "redirect_uri": request.redirect_uri,
        "sub": adapter.get_user_sub(client, request.user),
        "scopes": request.scopes,
        "claims": request.claims,
    }
    if email := getattr(request, "email", None):
        # Don't trouble ourselves with keeping track a specific email in case
        # the primary was chosen.
        if EmailAddress.objects.get_primary_email(request.user) != email.lower():
            authorization_code["email"] = email
    code_challenge = getattr(request, "code_challenge", None)
    if code_challenge:
        authorization_code["pkce"] = {
            "code_challenge": code_challenge,
            "code_challenge_method": request.code_challenge_method,
        }
    cache.set(
        cache_key(client.id, code["code"]),
        authorization_code,
        timeout=app_settings.AUTHORIZATION_CODE_EXPIRES_IN,
    )


def lookup(client_id: str, code: str) -> Optional[dict]:
    return cache.get(cache_key(client_id, code))


def invalidate(client_id: str, code: str) -> None:
    cache.delete(cache_key(client_id, code))


def validate(client_id: str, code: str, request) -> bool:
    authorization_code = lookup(client_id, code)
    if not authorization_code:
        return False
    user = get_adapter().get_user_by_sub(request.client, authorization_code["sub"])
    if not user:
        return False
    request.scopes = authorization_code["scopes"]
    request.user = user
    pkce = authorization_code.get("pkce")
    if pkce:
        request.code_challenge = pkce["code_challenge"]
        request.code_challenge_method = pkce["code_challenge_method"]
    request.claims = authorization_code["claims"]
    request.email = authorization_code.get("email")
    return True
