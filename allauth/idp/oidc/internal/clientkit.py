import re
from typing import List, Pattern
from urllib.parse import ParseResult, parse_qsl, urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_loopback(parsed_uri: ParseResult) -> bool:
    return parsed_uri.scheme == "http" and parsed_uri.hostname in (
        "127.0.0.1",
        "::1",
    )


def _validate_uri_wildcard_format(uri: str, allow_uri_wildcards: bool) -> None:
    if not allow_uri_wildcards:
        if "*" in uri:
            raise ValidationError(
                _("Wildcards are not allowed unless 'Allow URI wildcards' is enabled.")
            )
    elif uri.count("*") > 1:
        raise ValidationError(
            _(
                "URI '{}' contains more than one wildcard (*). Only one wildcard per URI is allowed."
            ).format(uri)
        )
    else:
        try:
            parsed = urlparse(uri)
        except ValueError as e:
            # it's possible for this to happen with wildcards in ports
            raise ValidationError(_("Invalid URI: {}".format(e)))

        if "*" in parsed.scheme or "*" in parsed.path or "*" in parsed.query:
            raise ValidationError(
                _("Wildcards are only allowed in the hostname portion of the URI.")
            )


def _wildcard_to_regex(wildcard: str) -> Pattern:
    pattern = re.escape(wildcard).replace(r"\*", r"[^.]+")
    return re.compile(f"^{pattern}$")


def _is_scheme_hostname_allowed(
    parsed_uri: ParseResult, parsed_allowed_uri: ParseResult, allow_uri_wildcards: bool
) -> bool:
    if parsed_allowed_uri.scheme != parsed_uri.scheme:
        return False

    if (
        allow_uri_wildcards
        and parsed_allowed_uri.hostname
        and "*" in parsed_allowed_uri.hostname
    ):
        allowed_hostname_pattern = _wildcard_to_regex(parsed_allowed_uri.hostname)

        if not allowed_hostname_pattern.match(parsed_uri.hostname):
            return False
    else:
        if parsed_allowed_uri.hostname != parsed_uri.hostname:
            return False

    return True


def is_parsed_redirect_uri_allowed(
    parsed_uri: ParseResult, allowed_uri: str, allow_uri_wildcards: bool
) -> bool:
    parsed_allowed_uri = urlparse(allowed_uri)

    if not _is_scheme_hostname_allowed(
        parsed_uri, parsed_allowed_uri, allow_uri_wildcards
    ):
        return False

    if parsed_allowed_uri.path != parsed_uri.path:
        return False

    if not is_loopback(parsed_allowed_uri):
        if parsed_allowed_uri.port != parsed_uri.port:
            return False

    if not set(parse_qsl(parsed_allowed_uri.query)).issubset(
        set(parse_qsl(parsed_uri.query))
    ):
        return False

    return True


def is_redirect_uri_allowed(
    uri: str, allowed_uris: List[str], allow_uri_wildcards: bool
) -> bool:
    parsed_uri = urlparse(uri)
    return any(
        is_parsed_redirect_uri_allowed(parsed_uri, allowed_uri, allow_uri_wildcards)
        for allowed_uri in allowed_uris
    )


def is_origin_allowed(
    origin: str, allowed_origins: List[str], allow_uri_wildcards: bool
) -> bool:
    parsed_origin = urlparse(origin)

    for allowed_origin in allowed_origins:
        parsed_allowed_origin = urlparse(allowed_origin)
        if (
            not _is_scheme_hostname_allowed(
                parsed_origin, parsed_allowed_origin, allow_uri_wildcards
            )
            or parsed_origin.username != parsed_allowed_origin.username
            or parsed_origin.password != parsed_allowed_origin.password
            or parsed_origin.port != parsed_allowed_origin.port
        ):
            continue
        else:
            return True

    return False
