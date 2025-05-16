from typing import List
from urllib.parse import ParseResult, parse_qsl, urlparse


def is_loopback(parsed_uri: ParseResult) -> bool:
    return parsed_uri.scheme == "http" and parsed_uri.hostname in (
        "127.0.0.1",
        "::1",
    )


def is_redirect_uri_allowed(uri: str, allowed_uris: List[str]) -> bool:
    parsed_uri = urlparse(uri)
    return any(
        is_parsed_redirect_uri_allowed(parsed_uri, allowed_uri)
        for allowed_uri in allowed_uris
    )


def is_parsed_redirect_uri_allowed(parsed_uri: ParseResult, allowed_uri: str) -> bool:
    parsed_allowed_uri = urlparse(allowed_uri)
    for field in ("scheme", "hostname", "path"):
        if getattr(parsed_allowed_uri, field) != getattr(parsed_uri, field):
            return False
    if not is_loopback(parsed_allowed_uri):
        if parsed_allowed_uri.port != parsed_uri.port:
            return False
    if not set(parse_qsl(parsed_allowed_uri.query)).issubset(
        set(parse_qsl(parsed_uri.query))
    ):
        return False
    return True


def is_origin_allowed(origin: str, allowed_origins: List[str]) -> bool:
    parsed_origin = urlparse(origin)
    for allowed_origin in allowed_origins:
        parsed_allowed_origin = urlparse(allowed_origin)
        if (
            parsed_allowed_origin.scheme == parsed_origin.scheme
            and parsed_allowed_origin.netloc == parsed_origin.netloc
        ):
            return True
    return False
