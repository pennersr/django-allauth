import time
import uuid
from datetime import timedelta

from django.utils import timezone

import pytest
from oauthlib.common import Request

from allauth.core.context import request_context
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib import authorization_codes
from allauth.idp.oidc.internal.oauthlib.request_validator import (
    OAuthLibRequestValidator,
)
from allauth.idp.oidc.internal.oauthlib.server import generate_jwt_access_token
from allauth.idp.oidc.models import Client, Token


@pytest.fixture
def oidc_client_secret():
    return uuid.uuid4().hex


@pytest.fixture
def oidc_client_factory(db, oidc_client_secret):
    def f(*, secret=None):
        client = Client.objects.create()
        client.set_secret(oidc_client_secret if secret is None else secret)
        client.set_redirect_uris(["https://rp.client/callback"])
        client.set_scopes(["profile", "openid", "email"])
        client.set_grant_types([g.value for g in Client.GrantType])
        client.set_response_types(["code", "token"])
        client.save()
        return client

    return f


@pytest.fixture
def oidc_client(oidc_client_secret, oidc_client_factory):
    return oidc_client_factory(secret=oidc_client_secret)


@pytest.fixture
def authorization_code_factory():
    def f(*, oidc_client, user, code, pkce=None):
        request = Request("https://server.example/authorize")
        request.redirect_uri = oidc_client.get_redirect_uris()[0]
        request.user = user
        request.scopes = ["openid"]
        request.claims = None
        if pkce:
            code_challenge = pkce["code_challenge"]
            request.code_challenge = (
                code_challenge.decode()
                if isinstance(code_challenge, bytes)
                else code_challenge
            )
            request.code_challenge_method = pkce["code_challenge_method"]
        authorization_codes.create(
            oidc_client,
            {"code": code},
            request,
            resources=None,
            email=None,
        )

    return f


@pytest.fixture
def device_client(db):
    client = Client.objects.create()
    client.type = Client.Type.PUBLIC
    client.set_redirect_uris(["https://client/callback"])
    client.set_scopes(["profile", "openid", "email"])
    client.set_grant_types([g.value for g in Client.GrantType])
    client.set_response_types(["code", "token"])
    client.save()
    return client


@pytest.fixture
def id_token_factory(rf):
    def f(client, user):
        with request_context(rf.get("/")):
            request = Request("/")
            request.scopes = ["openid"]
            request.user = user
            request.client = client
            return OAuthLibRequestValidator().finalize_id_token(
                {
                    "aud": client.id,
                    "iat": int(time.time()),
                },
                {},
                None,
                request,
            )

    return f


@pytest.fixture
def access_token_factory(access_token_format, rf):
    def f(client, user, scopes=["openid"], resources=None, expires_at=None):
        if access_token_format == "jwt":
            o_request = Request("/")
            o_request.user = user
            o_request.client = client
            request = rf.get("/")
            request.user = user
            with request_context(request):
                token = generate_jwt_access_token(o_request)
        else:
            token = uuid.uuid4().hex
        token_hash = get_adapter().hash_token(token)
        instance = Token(
            type=Token.Type.ACCESS_TOKEN,
            user=user,
            client=client,
            hash=token_hash,
            expires_at=expires_at,
        )
        instance.set_scopes(scopes)
        if resources:
            instance.set_resources(resources)
        instance.save()
        return token, instance

    return f


@pytest.fixture
def refresh_token_factory():
    def f(*, user, client, scopes=None):
        adapter = get_adapter()
        value = uuid.uuid4().hex
        rt = Token.objects.create(
            client=client,
            user=user,
            type=Token.Type.REFRESH_TOKEN,
            hash=adapter.hash_token(value),
            expires_at=timezone.now() + timedelta(seconds=60),
        )
        if scopes is None:
            scopes = ["openid", "profile"]
        rt.set_scopes(scopes)
        rt.set_grant_id(uuid.uuid4().hex)
        rt.save()
        return value, rt

    return f


@pytest.fixture(params=["jwt", "opaque"])
def access_token_format(request, settings) -> str:
    fmt = request.param
    settings.IDP_OIDC_ACCESS_TOKEN_FORMAT = fmt
    return fmt
