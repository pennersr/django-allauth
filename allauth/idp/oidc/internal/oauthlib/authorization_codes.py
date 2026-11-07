from __future__ import annotations

import uuid
from typing import Any

from django.core.cache import cache
from django.db import transaction

from oauthlib.common import Request

from allauth.account.models import EmailAddress
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib.utils import get_validator_context
from allauth.idp.oidc.models import Client, Token


def _cache_key(client_id: str, code: str) -> str:
    return f"allauth.idp.oidc.authorization_code[{client_id}:{code}]"


def _claim_cache_key(client_id: str, code: str) -> str:
    return f"{_cache_key(client_id, code)}.claim"


def _reuse_cache_key(client_id: str, code: str) -> str:
    return f"{_cache_key(client_id, code)}.reuse"


def _revoke_tokens(client_id: str, user_id: Any, grant_id: str) -> None:
    """
    https://datatracker.ietf.org/doc/html/rfc6749#section-10.5

    Authorization codes MUST be short lived and single-use.  If the
    authorization server observes multiple attempts to exchange an authorization
    code for an access token, the authorization server SHOULD attempt to revoke
    all access tokens already granted based on the compromised authorization
    code.
    """
    Token.objects.filter(
        client_id=client_id,
        user_id=user_id,
        type__in=[Token.Type.ACCESS_TOKEN, Token.Type.REFRESH_TOKEN],
        data__grant_id=grant_id,
    ).delete()


def _revoke_tokens_if_reused(
    client_id: str, code: str, user_id: Any, grant_id: str
) -> None:
    if cache.get(_reuse_cache_key(client_id, code)):
        _revoke_tokens(client_id, user_id, grant_id)


def _register_reuse(client_id: str, code: str, user_id: Any, grant_id: str) -> None:
    timeout = app_settings.AUTHORIZATION_CODE_EXPIRES_IN
    cache.add(_reuse_cache_key(client_id, code), True, timeout=timeout)
    # If the first redemption is still in a concurrent transaction, the tokens
    # are not visible yet. Whichever transaction commits last will perform the
    # check after its tokens can be observed.
    transaction.on_commit(lambda: _revoke_tokens(client_id, user_id, grant_id))


def create(
    client: Client,
    code: dict[str, Any],
    request: Request,
    *,
    resources: list[str] | None,
    email: str | None,
) -> str:
    adapter = get_adapter()
    grant_id = uuid.uuid4().hex
    authorization_code = {
        "code": code,
        "client_id": client.id,
        "redirect_uri": request.redirect_uri,
        "sub": adapter.get_user_sub(client, request.user),
        "scopes": request.scopes,
        "claims": request.claims,
        "resources": resources,
        "grant_id": grant_id,
    }
    if email:
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
        _cache_key(client.id, code["code"]),
        authorization_code,
        timeout=app_settings.AUTHORIZATION_CODE_EXPIRES_IN,
    )
    return grant_id


def lookup(client_id: str, code: str) -> dict[str, Any] | None:
    return cache.get(_cache_key(client_id, code))


def claim(client_id: str, code: str, request: Request) -> bool:
    """
    Claim the authorization code. Note that due to oauthlib call order,
    validation already happened at this point.
    """
    authorization_code = get_validator_context().codes.get((client_id, code))
    if authorization_code is None:
        raise RuntimeError("Authorization code was not validated before claiming")
    claimed = cache.add(
        _claim_cache_key(client_id, code),
        authorization_code,
        timeout=app_settings.AUTHORIZATION_CODE_EXPIRES_IN,
    )
    if claimed:
        return True
    # We have a valid code, but couldn't claim it. So it is being reused.
    # See https://datatracker.ietf.org/doc/html/rfc6749#section-10.5 --
    # register that reuse.
    _register_reuse(client_id, code, request.user.pk, authorization_code["grant_id"])
    return False


def invalidate(client_id: str, code: str, user_id: Any, grant_id: str) -> None:
    # We don't delete the code's `_cache_key()`. -- this way, validate() can
    # distinguish reuse from a code that was never valid.
    transaction.on_commit(
        lambda: _revoke_tokens_if_reused(client_id, code, user_id, grant_id)
    )


def validate(client_id: str, code: str, request: Request) -> bool:
    """
    Validate authorization code data. Note that a successful validation
    does not check code reuse or claim success.
    """
    ctx = get_validator_context()
    authorization_code = lookup(client_id, code)
    if authorization_code is None:
        claim_data = cache.get(_claim_cache_key(client_id, code))
        if isinstance(claim_data, dict):
            authorization_code = claim_data
    if authorization_code is None:
        return False
    ctx.codes[(client_id, code)] = authorization_code
    user = get_adapter().get_user_by_sub(request.client, authorization_code["sub"])
    if not user:
        return False
    grant_id = authorization_code.get("grant_id")
    if not isinstance(grant_id, str):
        return False
    request.scopes = authorization_code["scopes"]
    ctx.granted_resources = authorization_code["resources"]
    ctx.grant_id = grant_id
    request.user = user
    pkce = authorization_code.get("pkce")
    if pkce:
        request.code_challenge = pkce["code_challenge"]
        request.code_challenge_method = pkce["code_challenge_method"]
    request.claims = authorization_code["claims"]
    ctx.email = authorization_code.get("email")
    return True
