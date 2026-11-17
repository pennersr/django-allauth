from unittest.mock import patch

from allauth.core.internal import jwkkit
from tests.projects.common.settings import IDP_OIDC_PRIVATE_KEY


def test_load_jwk_from_pem_parses_each_pem_once():
    jwkkit._load_jwk_from_pem.cache_clear()
    with patch.object(jwkkit, "load_pem", wraps=jwkkit.load_pem) as load_pem:
        first, first_key = jwkkit.load_jwk_from_pem(IDP_OIDC_PRIVATE_KEY)
        second, second_key = jwkkit.load_jwk_from_pem(IDP_OIDC_PRIVATE_KEY)
    assert load_pem.call_count == 1
    assert first == second and first_key is second_key
    assert first["kid"] == jwkkit.jwk_thumbprint(first)


def test_load_jwk_from_pem_returns_a_copy_of_the_jwk():
    jwk_dict, _ = jwkkit.load_jwk_from_pem(IDP_OIDC_PRIVATE_KEY)
    jwk_dict["kid"] = "changed"
    again, _ = jwkkit.load_jwk_from_pem(IDP_OIDC_PRIVATE_KEY)
    assert again["kid"] != "changed"
