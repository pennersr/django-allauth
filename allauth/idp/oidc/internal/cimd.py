import json
import logging
import posixpath
import requests
import time
from http import HTTPStatus
from typing import Any
from urllib.parse import ParseResult, urlparse

from django.core.cache import cache
from django.core.exceptions import ValidationError

from allauth.core import context
from allauth.core.internal import ratelimit
from allauth.idp.oidc import app_settings
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Client


logger = logging.getLogger(__name__)

FETCH_TIMEOUT = 1
MAX_RESPONSE_SIZE = 2 * 1024


def is_cimd_url(client_id: str) -> bool:
    # Intentionally check for lower case, we don't want any '?client_id=HtTps://...' hacking
    return client_id.startswith("https:")


def validate_client_id(client_id: str) -> ParseResult:
    parsed = urlparse(client_id)
    if parsed.scheme != "https":
        raise ValidationError("client_id must use the https scheme.")
    if not parsed.hostname:
        raise ValidationError("client_id must contain a hostname.")
    if parsed.netloc != parsed.netloc.lower():
        raise ValidationError("client_id hostname must be lowercase.")
    if not parsed.path or parsed.path == "/":
        raise ValidationError("client_id must contain a path component.")
    if posixpath.normpath(parsed.path) != parsed.path:
        raise ValidationError("client_id path is not normalized.")
    if parsed.query:
        raise ValidationError("client_id must not contain a query component.")
    if parsed.fragment:
        raise ValidationError("client_id must not contain a fragment.")
    if parsed.username or parsed.password:
        raise ValidationError("client_id must not contain credentials.")
    client_id_max_length = Client.id.field.max_length
    assert client_id_max_length  # nosec
    if len(client_id) > client_id_max_length:
        raise ValidationError(
            f"client_id exceeds maximum length of {client_id_max_length}."
        )
    if not get_adapter().is_cimd_url_allowed(client_id):
        raise ValidationError("This client_id URL is not permitted by the server.")
    return parsed


def fetch_metadata_safely(client_id: str) -> Any:
    if not ratelimit.consume(
        context.request,
        action="cimd_fetch",
        app="allauth.idp.oidc",
        limit_get=True,
    ):
        raise ValidationError("CIMD fetch rate limited.")
    lock_key = f"allauth.cimd.fetch:{client_id}"
    if not cache.add(lock_key, True, timeout=FETCH_TIMEOUT + 5):
        raise ValidationError("CIMD fetch already in progress.")
    try:
        return fetch_metadata(client_id)
    finally:
        cache.delete(lock_key)


def fetch_metadata(client_id: str) -> Any:
    resp = requests.get(
        client_id,
        timeout=FETCH_TIMEOUT,
        headers={"Accept": "application/json"},
        stream=True,
        allow_redirects=False,
    )

    try:
        if resp.status_code != HTTPStatus.OK:
            raise ValidationError(f"CIMD fetch returned HTTP {resp.status_code}.")

        content_length = resp.headers.get("Content-Length")
        if (
            content_length
            and content_length.isdigit()
            and int(content_length) > MAX_RESPONSE_SIZE
        ):
            raise ValidationError("CIMD response too large.")

        body = next(resp.iter_content(chunk_size=MAX_RESPONSE_SIZE + 1), b"")
        if len(body) > MAX_RESPONSE_SIZE:
            raise ValidationError("CIMD response too large.")
    finally:
        resp.close()

    try:
        return json.loads(body)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"CIMD response is not valid JSON: {e}") from e


def fetch_client(client_id: str) -> Client:
    """
    Fetch a Client ID Metadata Document (CIMD) and return a Client instance.

    The ``client_id`` is expected to be an HTTPS URL pointing at a JSON metadata
    document whose ``client_id`` field matches the URL.

    Raises ``ValidationError`` for invalid client_id URLs or metadata, and
    ``requests.RequestException`` if the HTTP fetch fails.
    """
    parsed = validate_client_id(client_id)
    metadata = fetch_metadata_safely(client_id)
    return validate_metadata(client_id, parsed, metadata)


def _get_list_of_str(
    metadata: dict, field: str, dflt: list[str] | None = None
) -> list[str]:
    if field not in metadata and dflt is not None:
        return dflt
    value = metadata.get(field)
    if (
        not value
        or not isinstance(value, list)
        or not all(isinstance(item, str) for item in value)
    ):
        raise ValidationError(f"'{field}' must be a non-empty list of strings.")
    return value


def validate_metadata(client_id: str, parsed: ParseResult, metadata: Any) -> Client:
    if not isinstance(metadata, dict):
        raise ValidationError("CIMD document must be a JSON object.")
    if metadata.get("client_id") != client_id:
        raise ValidationError("'client_id' in CIMD document does not match the URL.")

    scope = metadata.get("scope", "openid")
    if not isinstance(scope, str):
        raise ValidationError("'scope' must be a string.")
    scopes = scope.split()

    name = metadata.get("client_name", parsed.hostname)
    if not isinstance(name, str):
        raise ValidationError("'client_name' must be a string.")
    name = name[: Client.name.field.max_length]

    grant_types = _get_list_of_str(metadata, "grant_types", ["authorization_code"])
    redirect_uris = _get_list_of_str(metadata, "redirect_uris")
    response_types = _get_list_of_str(metadata, "response_types", ["code"])
    _get_list_of_str(metadata, "post_logout_redirect_uris", [])
    client = Client(
        id=client_id,
        name=name,
        type=Client.Type.PUBLIC,
    )
    client.set_grant_types(grant_types)
    client.set_redirect_uris(redirect_uris)
    client.set_scopes(scopes)
    client.set_response_types(response_types)

    client.data = {
        "cimd": True,
        "client_metadata": metadata,
        "updated_at": int(time.time()),
    }
    return client


def is_outdated(client: Client) -> bool:
    updated_at = (client.data or {}).get("updated_at", 0)
    return time.time() - updated_at > app_settings.CIMD_CACHE_TIMEOUT


def lookup_client(client_id: str, client: Client | None) -> Client | None:
    if not is_cimd_url(client_id):
        return client
    if client and not is_outdated(client):
        return client
    try:
        updated_client = fetch_client(client_id)
    except (ValidationError, requests.RequestException):
        logger.warning("Failed to fetch CIMD for client_id: %s", client_id)
        return client
    updated_client._state.adding = client is None
    updated_client.save()
    return updated_client
