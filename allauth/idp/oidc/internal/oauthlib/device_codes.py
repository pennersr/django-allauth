import time
from typing import List, Optional, Tuple

from django.core.cache import cache
from django.http import HttpRequest

from oauthlib.oauth2.rfc6749.errors import (
    InvalidClientError,
    InvalidGrantError,
    InvalidRequestError,
    UnsupportedGrantTypeError,
)
from oauthlib.oauth2.rfc8628.errors import (
    AccessDenied,
    AuthorizationPendingError,
    SlowDownError,
)

from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.account.internal.userkit import user_id_to_str
from allauth.core.internal.cryptokit import compare_user_code
from allauth.idp.oidc.models import Client


def cache_user_code_key(user_code: str):
    return f"allauth.idp.oidc.user_code[{user_code.lower()}]"


def cache_device_code_key(device_code: str):
    return f"allauth.idp.oidc.device_code[{device_code}]"


def create(client_id: str, scope: Optional[List[str]], data: dict):
    cache.set(
        cache_user_code_key(data["user_code"]),
        data["device_code"],
        timeout=data["expires_in"],
    )
    cache.set(
        cache_device_code_key(data["device_code"]),
        {
            "expires_at": time.time() + data["expires_in"],
            "granted": None,
            "last_poll_at": 0,
            "client_id": client_id,
            "scope": scope,
            "device": data,
        },
        timeout=data["expires_in"],
    )


def lookup_client(client_id: str) -> Optional[Client]:
    client = Client.objects.filter(id=client_id).first()
    if not client:
        return None
    if client.type != Client.Type.PUBLIC:
        return None
    return client


def validate_user_code(code: str) -> Tuple[str, Client]:
    data: Optional[dict] = None
    device_code = cache.get(cache_user_code_key(code))
    if device_code:
        data = cache.get(cache_device_code_key(device_code))
    if (
        not data
        or data["granted"] is not None
        or not compare_user_code(actual=code, expected=data["device"]["user_code"])
    ):
        raise get_account_adapter().validation_error("incorrect_code")
    client = lookup_client(data["client_id"])
    if not client:
        raise get_account_adapter().validation_error("incorrect_code")
    return device_code, client


def confirm_or_deny_device_code(user, device_code: str, confirm: bool) -> bool:
    data = cache.get(cache_device_code_key(device_code))
    if data is None or data["granted"] is not None:
        return False
    data["granted"] = confirm
    data["user"] = user_id_to_str(user)
    return update_device_state(device_code, data)


def update_device_state(device_code: str, data: dict) -> bool:
    timeout = int(data["expires_at"] - time.time())
    if timeout < 0:
        return False
    cache.set(cache_device_code_key(device_code), data, timeout=timeout)
    return True


def poll_device_code(
    request: HttpRequest,
) -> dict:
    client_id = request.POST.get("client_id")
    device_code = request.POST.get("device_code")
    if not client_id or not device_code:
        raise InvalidRequestError
    client = lookup_client(client_id)
    if not client:
        raise InvalidClientError
    if client.GrantType.DEVICE_CODE not in client.get_grant_types():
        raise UnsupportedGrantTypeError
    cache_key = cache_device_code_key(device_code)
    data = cache.get(cache_key)
    if data is None or data["client_id"] != client_id:
        raise InvalidGrantError
    now = time.time()
    if data["last_poll_at"] + data["device"]["interval"] > now:
        raise SlowDownError
    data["last_poll_at"] = now
    update_device_state(device_code, data)
    granted = data.get("granted")
    if granted is None:
        raise AuthorizationPendingError
    elif granted is False:
        raise AccessDenied
    assert granted is True  # nosec
    cache.delete(cache_key)
    return data
