from __future__ import annotations

import uuid
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from oauthlib.common import Request

from allauth.account.models import EmailAddress
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.internal.oauthlib.utils import get_validator_context
from allauth.idp.oidc.models import Client, Token, TokenQuerySet


def _get_token_queryset(client_id: str, code: str) -> TokenQuerySet:
    return (
        Token.objects.valid()
        .by_value(code)
        .filter(client_id=client_id, type=Token.Type.AUTHORIZATION_CODE)
    )


def lookup(client_id: str, code: str) -> Token | None:
    return _get_token_queryset(client_id, code).first()


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
    token = lookup(client_id, code)
    if token and isinstance(token.data, dict) and token.data.get("reused") is True:
        _revoke_tokens(client_id, user_id, grant_id)


def _register_reuse(
    client_id: str,
    code: str,
    user_id: Any,
    grant_id: str,
    code_token: Token,
) -> None:
    data = code_token.data
    assert isinstance(data, dict)  # nosec[assert_used]
    _get_token_queryset(client_id, code).update(
        data=dict(data, claimed=True, reused=True)
    )
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
    grant_id = uuid.uuid4().hex
    data = {
        "claims": request.claims,
        "claimed": False,
    }
    code_challenge = getattr(request, "code_challenge", None)
    if code_challenge:
        data["pkce"] = {
            "code_challenge": code_challenge,
            "code_challenge_method": request.code_challenge_method,
        }
    token = Token(
        client=client,
        user=request.user,
        type=Token.Type.AUTHORIZATION_CODE,
        data=data,
        expires_at=timezone.now()
        + timedelta(seconds=app_settings.AUTHORIZATION_CODE_EXPIRES_IN),
    )
    token.set_value(code["code"])
    token.set_scopes(request.scopes)
    token.set_grant_id(grant_id)
    token.set_redirect_uri(request.redirect_uri)
    nonce = code.get("nonce")
    if nonce:
        token.set_nonce(nonce)
    if resources is not None:
        token.set_resources(resources)
    if email:
        # Don't trouble ourselves with keeping track a specific email in case
        # the primary was chosen.
        if EmailAddress.objects.get_primary_email(request.user) != email.lower():
            token.set_scope_email(email)
    token.save()
    return grant_id


def claim(client_id: str, code: str, request: Request) -> bool:
    """
    Claim the authorization code. Note that due to oauthlib call order,
    validation already happened at this point.
    """
    code_token = get_validator_context().code_tokens.get((client_id, code))
    if code_token is None:
        raise RuntimeError("Authorization code was not validated before claiming")

    data = code_token.data
    assert isinstance(data, dict)  # nosec[assert_used]
    claimed = (
        _get_token_queryset(client_id, code)
        .filter(data__claimed=False)
        .update(
            data=dict(data, claimed=True),
            # Retain a claimed code long enough to recognize a reuse attempt.
            expires_at=timezone.now()
            + timedelta(seconds=app_settings.AUTHORIZATION_CODE_EXPIRES_IN),
        )
    )
    if claimed:
        return True
    # We have a valid code, but couldn't claim it. So it is being reused.
    # See https://datatracker.ietf.org/doc/html/rfc6749#section-10.5 --
    # register that reuse.
    grant_id = code_token.get_grant_id()
    assert grant_id is not None  # nosec[assert_used]
    _register_reuse(
        client_id,
        code,
        request.user.pk,
        grant_id,
        code_token,
    )
    return False


def invalidate(client_id: str, code: str, user_id: Any, grant_id: str) -> None:
    transaction.on_commit(
        lambda: _revoke_tokens_if_reused(client_id, code, user_id, grant_id)
    )


def validate(client_id: str, code: str, request: Request) -> bool:
    """
    Validate authorization code data. Note that a successful validation
    does not check code reuse or claim success.
    """
    ctx = get_validator_context()
    code_token = _get_token_queryset(client_id, code).select_for_update().first()
    if code_token is None:
        return False
    ctx.code_tokens[(client_id, code)] = code_token
    user = code_token.user
    if not user:
        return False
    grant_id = code_token.get_grant_id()
    if grant_id is None:
        return False
    request.scopes = code_token.get_scopes()
    ctx.granted_resources = code_token.get_resources()
    ctx.grant_id = grant_id
    request.user = user
    data = code_token.data
    if not isinstance(data, dict):
        return False
    pkce = data.get("pkce")
    if pkce:
        request.code_challenge = pkce["code_challenge"]
        request.code_challenge_method = pkce["code_challenge_method"]
    request.claims = data["claims"]
    ctx.email = code_token.get_scope_email()
    return True
