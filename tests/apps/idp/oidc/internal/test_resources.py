from django.core.exceptions import ValidationError

import pytest

from allauth.idp.oidc.internal.resources import is_resources_subset, validate_resources


@pytest.mark.parametrize(
    "requested,granted,expected",
    [
        # No granted resources means anything is allowed.
        (["https://api.example.com/a"], [], True),
        # No requested resources is always fine.
        ([], ["https://api.example.com"], True),
        # Exact match.
        (["https://api.example.com/a"], ["https://api.example.com/a"], True),
        # Sub-path is allowed.
        (["https://api.example.com/a/b"], ["https://api.example.com/a"], True),
        # Different path is not allowed.
        (["https://api.example.com/b"], ["https://api.example.com/a"], False),
        # Prefix match must respect path boundaries — /ninja does not grant /ninja-admin.
        (
            ["https://api.example.com/ninja-admin"],
            ["https://api.example.com/ninja"],
            False,
        ),
        # But /ninja does grant /ninja/sub.
        (
            ["https://api.example.com/ninja/sub"],
            ["https://api.example.com/ninja"],
            True,
        ),
        # Different scheme.
        (["http://api.example.com/a"], ["https://api.example.com/a"], False),
        # Different host.
        (["https://other.example.com/a"], ["https://api.example.com/a"], False),
    ],
)
def test_is_resources_subset(requested, granted, expected):
    assert is_resources_subset(requested, granted) == expected


@pytest.mark.parametrize(
    "resource",
    [
        # Valid absolute URI.
        "https://api.example.com/a",
        # A trailing slash is valid for an RFC 8707 resource URI.
        "https://api.example.com/a/",
        # Valid with no path.
        "https://api.example.com",
    ],
)
def test_validate_resources(resource):
    validate_resources([resource])


@pytest.mark.parametrize(
    "resource",
    [
        # Missing scheme — not absolute.
        "api.example.com/a",
        # Missing netloc — not absolute.
        "/a/b/c",
        # Fragment not allowed.
        "https://api.example.com/a#frag",
        # Directory traversal.
        "https://api.example.com/a/../b",
        # Non-normalized path with double slash.
        "https://api.example.com//a",
        # Non-normalized path with dot segment.
        "https://api.example.com/./a",
        # Trailing dot-dot.
        "https://api.example.com/a/..",
    ],
)
def test_validate_resources_invalid(resource):
    with pytest.raises(ValidationError):
        validate_resources([resource])
