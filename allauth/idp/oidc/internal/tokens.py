from typing import Optional

import jwt

from allauth.core.internal import jwkkit
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter


def decode_jwt_token(
    value: str, *, client_id: Optional[str] = None, verify_exp: bool, verify_iss: bool
) -> Optional[dict]:
    if not value:
        return None
    try:
        jwk_dict, private_key = jwkkit.load_jwk_from_pem(app_settings.PRIVATE_KEY)
        issuer: str | None = None
        audience: str | None = None
        if client_id:
            audience = client_id
        if verify_iss:
            issuer = get_adapter().get_issuer()
        return jwt.decode(
            value,
            key=private_key.public_key(),
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_iss": verify_iss,
                "verify_aud": client_id is not None,
                "verify_exp": verify_exp,
            },
            audience=audience,
            issuer=issuer,
        )
    except jwt.PyJWTError:
        return None
