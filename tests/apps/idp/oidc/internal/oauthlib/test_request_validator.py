import pytest
from oauthlib.common import Request

from allauth.core.context import request_context
from allauth.idp.oidc.internal.oauthlib.request_validator import (
    OAuthLibRequestValidator,
)


@pytest.mark.parametrize(
    "origin,allowed_origins,is_allowed",
    [
        ("http://origin", ["https://origin"], False),
        ("https://origin", ["https://origin"], True),
        ("https://origin", [], False),
        ("https://origin", ["https://notthis", "https://origin"], True),
    ],
)
def test_is_origin_allowed(origin, allowed_origins, is_allowed, oidc_client, rf):
    oidc_client.set_cors_origins(allowed_origins)
    oidc_client.save()
    request = rf.get("/")
    orequest = Request("/")
    with request_context(request):
        assert (
            OAuthLibRequestValidator().is_origin_allowed(
                oidc_client.id, origin, orequest
            )
            == is_allowed
        )


def test_default_scopes(settings, oidc_client, rf):
    settings.IDP_OIDC_DEFAULT_SCOPES = ["openid", "email"]
    orequest = Request("/")
    orequest.client = oidc_client
    with request_context(rf.get("/")):
        validator = OAuthLibRequestValidator()
        assert validator.get_default_scopes(oidc_client.id, orequest) == [
            "openid",
            "email",
        ]

        oidc_client.set_default_scopes(["profile"])
        assert validator.get_default_scopes(oidc_client.id, orequest) == ["profile"]


def test_validate_scopes_rejects_empty(oidc_client):
    orequest = Request("/")
    orequest.client = oidc_client
    validator = OAuthLibRequestValidator()
    assert not validator.validate_scopes(oidc_client.id, [], oidc_client, orequest)


@pytest.mark.parametrize(
    "default_scopes", [[], ["openid", "email"], ["openid", "unsupported"]]
)
def test_invalid_default_scopes(settings, oidc_client, rf, default_scopes):
    settings.IDP_OIDC_DEFAULT_SCOPES = default_scopes
    oidc_client.set_scopes(["openid"])
    orequest = Request("/")
    orequest.client = oidc_client

    with request_context(rf.get("/")):
        validator = OAuthLibRequestValidator()
        scopes = validator.get_default_scopes(oidc_client.id, orequest)

    assert scopes == []
    assert not validator.validate_scopes(oidc_client.id, scopes, oidc_client, orequest)
