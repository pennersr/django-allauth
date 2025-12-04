import json
import time

from django.core.cache import cache

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Error


def lookup_kid_pem_x509_certificate(keys_data, kid):
    """
    Looks up the key given keys data of the form:

        {"<kid>": "-----BEGIN CERTIFICATE-----\nCERTIFICATE"}
    """
    key = keys_data.get(kid)
    if key:
        public_key = load_pem_x509_certificate(
            key.encode("utf8"), default_backend()
        ).public_key()
        return public_key


def lookup_kid_jwk(keys_data, kid):
    """
    Looks up the key given keys data of the form:

        {
          "keys": [
            {
              "kty": "RSA",
              "kid": "W6WcOKB",
              "use": "sig",
              "alg": "RS256",
              "n": "2Zc5d0-zk....",
              "e": "AQAB"
            }]
        }
    """
    for d in keys_data["keys"]:
        if d["kid"] == kid:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(d))
            return public_key


def fetch_key(credential, keys_url, lookup):
    header = jwt.get_unverified_header(credential)
    # {'alg': 'RS256', 'kid': '0ad1fec78504f447bae65bcf5afaedb65eec9e81', 'typ': 'JWT'}
    kid = header["kid"]
    alg = header["alg"]
    with get_adapter().get_requests_session() as sess:
        response = sess.get(keys_url)
        response.raise_for_status()
        keys_data = response.json()
    key = lookup(keys_data, kid)
    if not key:
        raise OAuth2Error(f"Invalid 'kid': '{kid}'")
    return alg, key


def verify_jti(data: dict) -> None:
    """
    Put the JWT token on a blacklist to prevent replay attacks.
    """
    iss = data.get("iss")
    exp = data.get("exp")
    jti = data.get("jti")
    if iss is None or exp is None or jti is None:
        return
    timeout = exp - time.time()
    key = f"jwt:iss={iss},jti={jti}"
    if not cache.add(key=key, value=True, timeout=timeout):
        raise OAuth2Error("token already used")


def verify_and_decode(
    *, credential, keys_url, issuer, audience, lookup_kid, verify_signature=True
):
    try:
        if verify_signature:
            alg, key = fetch_key(credential, keys_url, lookup_kid)
            algorithms = [alg]
        else:
            key = ""
            algorithms = None
        data = jwt.decode(
            credential,
            key=key,
            options={
                "verify_signature": verify_signature,
                "verify_iss": True,
                "verify_aud": True,
                "verify_exp": True,
            },
            issuer=issuer,
            audience=audience,
            algorithms=algorithms,
        )
        verify_jti(data)
        return data
    except jwt.PyJWTError as e:
        raise OAuth2Error("Invalid id_token") from e
