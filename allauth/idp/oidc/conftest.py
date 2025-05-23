import time
import uuid
from datetime import timedelta
from types import SimpleNamespace

from django.utils import timezone

import pytest

from allauth.core.context import request_context
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.internal.oauthlib.request_validator import (
    OAuthLibRequestValidator,
)
from allauth.idp.oidc.models import Client, Token


@pytest.fixture
def oidc_client_secret():
    return uuid.uuid4().hex


@pytest.fixture
def oidc_client(db, oidc_client_secret):
    client = Client.objects.create()
    client.set_secret(oidc_client_secret)

    client.set_redirect_uris(["https://client/callback"])
    client.set_scopes(["profile", "openid", "email"])
    client.set_grant_types(
        ["authorization_code", "client_credentials", "password", "refresh_token"]
    )
    client.set_response_types(["code", "token"])
    client.save()
    return client


@pytest.fixture
def id_token_generator(rf):
    def f(client, user):
        with request_context(rf.get("/")):
            request = SimpleNamespace(client=client, user=user, scopes=["openid"])
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
def access_token_generator():
    def f(client, user, scopes=["openid"]):
        token = uuid.uuid4().hex
        token_hash = get_adapter().hash_token(token)
        instance = Token(
            type=Token.Type.ACCESS_TOKEN,
            user=user,
            client=client,
            hash=token_hash,
        )
        instance.set_scopes(scopes)
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
        rt.save()
        return value, rt

    return f
