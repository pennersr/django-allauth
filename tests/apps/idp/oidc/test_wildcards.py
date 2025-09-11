from django.core.exceptions import ValidationError

import pytest

from allauth.idp.oidc.internal.clientkit import (
    _wildcard_to_regex,
    is_origin_allowed,
    is_redirect_uri_allowed,
)
from allauth.idp.oidc.models import Client


URI_TEST_CASES = [
    (False, "https://example.com", True),
    (False, "https://*.example.com", False),
    (True, "https://example.com", True),
    (True, "https://*.projectname.pages.dev/", True),
    (True, "https://*--projectname-com.netlify.app", True),
    (True, "http://*.localhost:3000", True),
    (True, "https://example.com/callback", True),
    (True, "https://*.*.example.com", False),
    (True, "http*://example.com", False),
    (True, "https://example.com/callback/*", False),
]


@pytest.mark.parametrize(
    ("allow_wildcards", "uri", "should_pass"),
    URI_TEST_CASES,
)
def test_redirect_uri_wildcard_validation(allow_wildcards, uri, should_pass):
    client = Client(
        id="test-client",
        name="Test Client",
        allow_uri_wildcards=allow_wildcards,
        redirect_uris=uri,
    )

    if should_pass:
        client.clean_redirect_uris()
    else:
        with pytest.raises(ValidationError):
            client.clean_redirect_uris()


@pytest.mark.parametrize(
    ("allow_wildcards", "origin", "should_pass"),
    URI_TEST_CASES,
)
def test_cors_origin_wildcard_validation(allow_wildcards, origin, should_pass):
    client = Client(
        id="test-client",
        name="Test Client",
        allow_uri_wildcards=allow_wildcards,
        cors_origins=origin,
    )

    if should_pass:
        client.clean_cors_origins()
    else:
        with pytest.raises(ValidationError):
            client.clean_cors_origins()


def test_wildcards_disabled_by_default():
    client = Client(
        id="test-client",
        name="Test Client",
        redirect_uris="https://example.com",
    )

    assert client.allow_uri_wildcards is False

    client.redirect_uris = "https://*.example.com"
    with pytest.raises(ValidationError):
        client.clean_redirect_uris()


def test_wildcard_matching_enforcement():
    client = Client(
        id="test-client",
        name="Test Client",
        allow_uri_wildcards=True,
        redirect_uris="https://*.example.com/callback",
        cors_origins="https://*.example.com",
    )

    assert is_redirect_uri_allowed(
        "https://subdomain.example.com/callback",
        client.get_redirect_uris(),
        client.allow_uri_wildcards,
    )
    assert not is_redirect_uri_allowed(
        "https://evil-example.com/callback",
        client.get_redirect_uris(),
        client.allow_uri_wildcards,
    )

    assert is_origin_allowed(
        "https://subdomain.example.com",
        client.get_cors_origins(),
        client.allow_uri_wildcards,
    )

    assert not is_origin_allowed(
        "https://evil-example.com",
        client.get_cors_origins(),
        client.allow_uri_wildcards,
    )

    assert not is_origin_allowed(
        "https://user:pass@foo.example.com",
        client.get_cors_origins(),
        client.allow_uri_wildcards,
    )


def test_wildcard_to_regex():
    pattern = _wildcard_to_regex("*.example.com")
    assert pattern.pattern == r"^[^.]+\.example\.com$"

    assert pattern.match("api.example.com")
    assert not pattern.match("foo.api.example.com")  # * should not match dots
    assert not pattern.match("evil-example.com")

    # verify dots aren't treated as wildcards
    assert not pattern.match("api$example$com")
