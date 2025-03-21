import time
from dataclasses import dataclass
from typing import List

from django.contrib.auth.models import AbstractUser
from django.core.signing import BadSignature, Signer
from django.http import HttpRequest, HttpResponse
from django.utils.crypto import salted_hmac

from allauth.mfa import app_settings
from allauth.mfa.models import Authenticator


@dataclass
class IssuedTrust:
    fingerprint: str
    at: int


def create_config_fingerprint(user: AbstractUser) -> str:
    """
    If the user changes anything about his security setup, we want to invalidate
    any trust that was issued before.
    """
    salt = "allauth.mfa.trust"
    parts: List[str] = []
    parts.append(str(user.pk))
    parts.append(user.password)
    for authenticator in Authenticator.objects.filter(user_id=user.pk).order_by("pk"):
        parts.append(str(authenticator.pk))
        parts.append(str(authenticator.type))
        seed = authenticator.data.get("seed")
        if seed is not None:
            parts.append(str(seed))
    return salted_hmac(salt, "|".join(parts), algorithm="sha256").hexdigest()


def decode_trust_cookie(request: HttpRequest) -> List[IssuedTrust]:
    value = request.COOKIES.get(app_settings.TRUST_COOKIE_NAME)
    if not value:
        return []
    signer = Signer()
    try:
        data = signer.unsign_object(value)
    except BadSignature:
        return []
    trusts = [IssuedTrust(fingerprint=entry[0], at=entry[1]) for entry in data]
    now = time.time()
    trusts = list(
        filter(
            lambda t: t.at + app_settings.TRUST_COOKIE_AGE.total_seconds() > now, trusts
        )
    )
    return trusts


def encode_trust_cookie(trusts: List[IssuedTrust]) -> str:
    signer = Signer()
    return signer.sign_object([(it.fingerprint, it.at) for it in trusts])


def trust_browser(
    request: HttpRequest, user: AbstractUser, response: HttpResponse
) -> None:
    fingerprint = create_config_fingerprint(user)
    trusts = decode_trust_cookie(request)
    trusts.append(IssuedTrust(fingerprint=fingerprint, at=int(time.time())))
    response.set_cookie(
        app_settings.TRUST_COOKIE_NAME,
        encode_trust_cookie(trusts),
        max_age=app_settings.TRUST_COOKIE_AGE,
        path=app_settings.TRUST_COOKIE_PATH,
        domain=app_settings.TRUST_COOKIE_DOMAIN,
        secure=app_settings.TRUST_COOKIE_SECURE,
        httponly=app_settings.TRUST_COOKIE_HTTPONLY,
    )


def is_trusted_browser(request: HttpRequest, user: AbstractUser) -> bool:
    if not app_settings.TRUST_ENABLED:
        return False
    trusts = decode_trust_cookie(request)
    fingerprint = create_config_fingerprint(user)
    return any([t.fingerprint == fingerprint for t in trusts])
