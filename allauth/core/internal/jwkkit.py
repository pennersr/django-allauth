# https://github.com/jpadilla/pyjwt/issues/1032
import base64
import hashlib
import json
from typing import Tuple

import jwt
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from jwt.algorithms import RSAAlgorithm


# In lexicographic order as described in RFC7638
JWK_REQUIRED_MEMBERS = {
    "EC": ("crv", "kty", "x", "y"),
    "RSA": ("e", "kty", "n"),
    "oct": ("k", "kty"),
}


def jwk_thumbprint(jwk_dict: dict) -> str:
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


def load_pem(pem: str) -> RSAPrivateKey:
    private_key = load_pem_private_key(
        pem.encode("utf8"),
        password=None,
    )
    if not isinstance(private_key, RSAPrivateKey):
        raise ValueError
    return private_key


def load_jwk_from_pem(pem: str) -> Tuple[dict, RSAPrivateKey]:
    private_key = load_pem(pem)
    public_key = private_key.public_key()
    jwk_dict = json.loads(RSAAlgorithm.to_jwk(public_key))
    jwk_dict["kid"] = jwk_thumbprint(jwk_dict)
    return jwk_dict, private_key
