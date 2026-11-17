# https://github.com/jpadilla/pyjwt/issues/1032
from __future__ import annotations

import base64
import functools
import hashlib
import json
from typing import Any

from allauth.core.internal.deferred import cryptography, jwt


# In lexicographic order as described in RFC7638
JWK_REQUIRED_MEMBERS = {
    "EC": ("crv", "kty", "x", "y"),
    "RSA": ("e", "kty", "n"),
    "oct": ("k", "kty"),
}


def jwk_thumbprint(jwk_dict: dict[str, Any]) -> str:
    key_type = jwk_dict["kty"]
    members = JWK_REQUIRED_MEMBERS.get(key_type)
    if members is None:
        raise jwt.exceptions.PyJWKError(f"Unable to canonicalize key type {key_type}")
    json_bytes = json.dumps(
        {k: jwk_dict[k] for k in members},
        separators=(",", ":"),
    ).encode()
    json_hash = hashlib.sha256(json_bytes).digest()
    return base64.urlsafe_b64encode(json_hash).rstrip(b"=").decode()


def load_pem(pem: str) -> cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey:
    private_key = cryptography.hazmat.primitives.serialization.load_pem_private_key(
        pem.encode("utf8"),
        password=None,
    )
    if not isinstance(
        private_key, cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey
    ):
        raise ValueError
    return private_key


def load_jwk_from_pem(
    pem: str,
) -> tuple[dict[str, Any], cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey]:
    jwk_dict, private_key = _load_jwk_from_pem(pem)
    return dict(jwk_dict), private_key


@functools.lru_cache(maxsize=16)
def _load_jwk_from_pem(
    pem: str,
) -> tuple[dict[str, Any], cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKey]:
    # Loading a PEM validates the RSA key, which costs tens to hundreds of
    # milliseconds depending on the key size. The IdP does this for every token
    # it signs and for every JWKS request, so parse each PEM once per process.
    private_key = load_pem(pem)
    public_key = private_key.public_key()
    jwk_dict = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    jwk_dict["kid"] = jwk_thumbprint(jwk_dict)
    return jwk_dict, private_key
