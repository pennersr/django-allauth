import base64
import binascii
import hashlib
import secrets
import time
import uuid
from typing import Any, Dict, Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.base import SessionBase
from django.utils.functional import SimpleLazyObject

import jwt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from allauth.account.internal.userkit import str_to_user_id, user_id_to_str
from allauth.core.internal import jwkkit
from allauth.core.internal.sessionkit import get_session_user
from allauth.headless import app_settings
from allauth.headless.internal.sessionkit import lookup_session


def validate_access_token(token: str) -> Optional[Tuple[Any, Dict[str, Any]]]:
    payload = decode_token(token, "access")
    if payload is None:
        return None
    if app_settings.JWT_STATEFUL_VALIDATION_ENABLED:
        session = get_token_session(payload)
        if session is None:
            return None
    sub = payload["sub"]
    pk = str_to_user_id(sub)
    lazy_user = SimpleLazyObject(lambda: get_user_model().objects.get(pk=pk))
    return lazy_user, payload


def get_session_key_cipher(initialization_vector: bytes) -> Cipher:
    secret_key = settings.SECRET_KEY
    key = hashlib.sha256(secret_key.encode()).digest()
    algorithm = algorithms.AES(key)
    mode = modes.CTR(initialization_vector)
    cipher = Cipher(algorithm, mode)
    return cipher


def session_key_to_sid(session_key: str) -> str:
    """
    In case an access token leaks, we do not want the session encoded in
    that token to be put to use as an X-Session-Token or session
    cookie. Therefore, we encrypt the sesison key. Unauthenticated symmetric
    encryption is fine, as the JWT is signed.
    """
    initialization_vector = secrets.token_bytes(16)
    cipher = get_session_key_cipher(initialization_vector)
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(session_key.encode()) + encryptor.finalize()
    sid = base64.b64encode(initialization_vector + encrypted_message).decode()
    return sid


def session_key_from_sid(sid: str) -> Optional[str]:
    try:
        encrypted_data = base64.b64decode(sid)
    except binascii.Error:
        return None
    initialization_vector = encrypted_data[:16]
    encrypted_message = encrypted_data[16:]
    if len(encrypted_message) == 0:
        return None
    cipher = get_session_key_cipher(initialization_vector)
    decryptor = cipher.decryptor()
    message_decrypted = decryptor.update(encrypted_message) + decryptor.finalize()
    try:
        return message_decrypted.decode()
    except UnicodeDecodeError:
        return None


def validate_token_user(token: Dict[str, Any], session: SessionBase):
    user = get_session_user(session)
    if user is None:
        return None
    sub = user_id_to_str(user)
    if sub != token["sub"]:
        return None
    return user


def validate_refresh_token(
    token: str,
) -> Optional[Tuple[Any, SessionBase, Dict[str, Any]]]:
    payload = decode_token(token, "refresh")
    if payload is None:
        return None
    jti = payload["jti"]
    session = get_token_session(payload)
    if session is None:
        return None
    refresh_token_jti_to_exp = get_refresh_token_state(session)
    exp = refresh_token_jti_to_exp.get(jti)
    now = time.time()
    if exp is None or exp <= now:
        return None
    user = validate_token_user(payload, session)
    return user, session, payload


def get_token_session(payload: Dict[str, Any]) -> Optional[SessionBase]:
    sid = payload.get("sid")
    if not isinstance(sid, str):
        return None
    session_key = session_key_from_sid(sid)
    if not session_key:
        return None
    session = lookup_session(session_key)
    if session is None:
        return None
    return session


def decode_token(token: str, use: str) -> Optional[Dict[str, Any]]:
    try:
        jwk_dict, private_key = jwkkit.load_jwk_from_pem(app_settings.JWT_PRIVATE_KEY)
        payload = jwt.decode(
            token,
            key=private_key.public_key(),
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_iss": False,
                "verify_aud": False,
                "verify_exp": True,
            },
        )
    except jwt.PyJWTError:
        return None
    else:
        if payload.get("token_use") != use:
            return None
        for key in ("jti", "sub", "sid"):
            value = payload.get(key)
            if not isinstance(value, str):
                return None
        return payload


def create_token(
    token_use: str,
    *,
    sub: str,
    sid: str,
    claims: Optional[Dict[str, Any]] = None,
    expires_in: int,
) -> Tuple[str, Dict[str, Any]]:
    jwk_dict, private_key = jwkkit.load_jwk_from_pem(app_settings.JWT_PRIVATE_KEY)
    now = int(time.time())
    payload = {}
    if claims is not None:
        payload.update(claims)
    payload.update(
        {
            "iat": now,
            "exp": now + expires_in,
            "sid": sid,
            "jti": str(uuid.uuid4()),
            "token_use": token_use,
            "sub": sub,
        }
    )
    return (
        jwt.encode(
            payload,
            private_key,
            algorithm="RS256",
            headers={"kid": jwk_dict["kid"]},
        ),
        payload,
    )


def get_refresh_token_state(session: SessionBase) -> Dict[str, int]:
    return session.setdefault("headless_refresh_tokens", {})


def create_refresh_token(user, session: SessionBase) -> str:
    assert user.is_authenticated  # nosec
    assert session.session_key  # nosec
    sub = user_id_to_str(user)
    sid = session_key_to_sid(session.session_key)
    token, payload = create_token(
        "refresh",
        sub=sub,
        sid=sid,
        expires_in=app_settings.JWT_REFRESH_TOKEN_EXPIRES_IN,
    )
    refresh_token_jti_to_exp = get_refresh_token_state(session)
    refresh_token_jti_to_exp[payload["jti"]] = payload["exp"]
    return token


def create_access_token(user, session: SessionBase, claims: Dict[str, Any]) -> str:
    assert user.is_authenticated  # nosec
    assert session.session_key  # nosec
    sid = session_key_to_sid(session.session_key)
    sub = user_id_to_str(user)
    return create_token(
        "access",
        sub=sub,
        sid=sid,
        claims=claims,
        expires_in=app_settings.JWT_ACCESS_TOKEN_EXPIRES_IN,
    )[0]


def invalidate_refresh_token(session: SessionBase, token: Dict[str, Any]) -> None:
    refresh_token_jti_to_exp = get_refresh_token_state(session)
    jti = token["jti"]
    refresh_token_jti_to_exp.pop(jti, None)
