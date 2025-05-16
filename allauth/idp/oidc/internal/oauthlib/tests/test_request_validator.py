from types import SimpleNamespace

import pytest

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
def test_is_origin_allowed(origin, allowed_origins, is_allowed, oidc_client):
    oidc_client.set_cors_origins(allowed_origins)
    oidc_client.save()
    request = SimpleNamespace()
    assert (
        OAuthLibRequestValidator().is_origin_allowed(oidc_client.id, origin, request)
        == is_allowed
    )
