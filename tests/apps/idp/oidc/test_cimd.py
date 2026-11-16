import json
import requests
from http import HTTPStatus
from typing import Any
from unittest.mock import patch
from urllib.parse import urlparse

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured, ValidationError

import pytest

from allauth.idp.oidc.adapter import DefaultOIDCAdapter
from allauth.idp.oidc.internal import cimd
from allauth.idp.oidc.internal.clientkit import lookup_client
from allauth.idp.oidc.models import Client


CIMD_CLIENT_ID = "https://app.example.com/client-metadata"


class CIMDTestAdapter(DefaultOIDCAdapter):
    def is_cimd_url_allowed(self, url: str) -> bool:
        return "disallowed" not in url


class CIMDDefaultScopesTestAdapter(DefaultOIDCAdapter):
    def get_cimd_default_scopes(
        self,
        *,
        client: Client,
        client_metadata: dict[str, Any],
        **kwargs: Any,
    ) -> list[str]:
        return ["openid", "custom"]


@pytest.fixture
def cimd_enabled(settings):
    settings.IDP_OIDC_CIMD_ENABLED = True
    settings.IDP_OIDC_ADAPTER = "tests.apps.idp.oidc.test_cimd.CIMDTestAdapter"


@pytest.fixture
def requests_get_mock():
    with patch("allauth.idp.oidc.internal.cimd.requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def response_mock(requests_get_mock):
    mock_resp = requests_get_mock.return_value
    mock_resp.status_code = HTTPStatus.OK
    mock_resp.headers = {}
    yield mock_resp


def _validate_metadata(metadata, client_id=CIMD_CLIENT_ID):
    parsed = urlparse(client_id)
    return cimd.validate_metadata(client_id, parsed, metadata)


def _metadata_factory(**overrides):
    metadata = {
        "client_id": CIMD_CLIENT_ID,
        "redirect_uris": ["https://app.example.com/callback"],
        "client_name": "Example App",
        "scope": "openid profile",
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "post_logout_redirect_uris": ["https://app.example.com/logout"],
    }
    for k, v in overrides.items():
        if v is NotImplemented:
            metadata.pop(k, None)
        else:
            metadata[k] = v
    return metadata


@pytest.mark.parametrize(
    "client_id,expected",
    [
        ("https://example.com/app", True),
        ("http://example.com/app", False),
        ("HTTPS://example.com/app", False),
        ("my-client-id", False),
    ],
)
def test_is_cimd_url(client_id, expected):
    assert cimd.is_cimd_url(client_id) is expected


@pytest.mark.parametrize(
    "allowed_hosts,expected",
    [
        ([], False),
        (["app.example.com"], True),
        (["other.example.com"], False),
        (["*"], True),
    ],
)
def test_is_cimd_url_allowed(settings, rf, allowed_hosts, expected):
    settings.IDP_OIDC_CIMD_ALLOWED_HOSTS = allowed_hosts
    adapter = DefaultOIDCAdapter(rf.get("/"))
    assert adapter.is_cimd_url_allowed(CIMD_CLIENT_ID) is expected


@pytest.mark.parametrize(
    "client_id,error_match",
    [
        (CIMD_CLIENT_ID, None),
        (f"{CIMD_CLIENT_ID}/okay", None),
        (f"{CIMD_CLIENT_ID}/disallowed", "not permitted"),
        ("https://example.com", "path"),
        ("https://example.com/", "path"),
        ("https://example.com/app?foo=bar", "query"),
        ("https://example.com/app#frag", "fragment"),
        ("https://user:pass@example.com/app", "credentials"),
        ("https://Example.COM/app", "lowercase"),
        ("https://example.com/a/../b", "normalized"),
        ("https://example.com" + "/a" * 200, "maximum length"),
    ],
)
def test_validate_client_id(cimd_enabled, db, client_id, error_match):
    if error_match is None:
        parsed = cimd.validate_client_id(client_id)
        assert parsed.hostname == "app.example.com"
    else:
        with pytest.raises(ValidationError, match=error_match):
            cimd.validate_client_id(client_id)


def test_validate_metadata(db):
    client = _validate_metadata(_metadata_factory())
    assert client.id == CIMD_CLIENT_ID
    assert client.name == "Example App"
    assert client.type == Client.Type.PUBLIC
    assert client.get_scopes() == ["openid", "profile"]
    assert client.get_redirect_uris() == ["https://app.example.com/callback"]
    assert client.get_post_logout_redirect_uris() == ["https://app.example.com/logout"]
    assert client.get_grant_types() == ["authorization_code"]
    assert client.get_response_types() == ["code"]
    assert client.data["cimd"] is True


def test_validate_metadata_defaults(db):
    metadata = {
        "client_id": CIMD_CLIENT_ID,
        "redirect_uris": ["https://app.example.com/callback"],
    }
    client = _validate_metadata(metadata)
    assert client.get_scopes() == ["openid", "profile", "email"]
    assert client.get_grant_types() == ["authorization_code"]
    assert client.get_response_types() == ["code"]
    assert client.name == "app.example.com"
    # post_logout_redirect_uris is optional; when omitted, there are none.
    assert client.get_post_logout_redirect_uris() == []


def test_validate_metadata_configured_default_scopes(db, settings):
    settings.IDP_OIDC_CIMD_DEFAULT_SCOPES = ["openid", "email"]
    metadata = {
        "client_id": CIMD_CLIENT_ID,
        "redirect_uris": ["https://app.example.com/callback"],
    }
    client = _validate_metadata(metadata)
    assert client.get_scopes() == ["openid", "email"]


def test_validate_metadata_adapter_default_scopes(db, settings):
    settings.IDP_OIDC_ADAPTER = (
        "tests.apps.idp.oidc.test_cimd.CIMDDefaultScopesTestAdapter"
    )
    settings.IDP_OIDC_SCOPE_CHOICES = ["openid", "custom"]
    metadata = {
        "client_id": CIMD_CLIENT_ID,
        "redirect_uris": ["https://app.example.com/callback"],
    }
    client = _validate_metadata(metadata)
    assert client.get_scopes() == ["openid", "custom"]


def test_validate_metadata_invalid_default_scopes(db, settings):
    settings.IDP_OIDC_CIMD_DEFAULT_SCOPES = ["openid", "unsupported"]
    metadata = {
        "client_id": CIMD_CLIENT_ID,
        "redirect_uris": ["https://app.example.com/callback"],
    }
    with pytest.raises(ImproperlyConfigured, match="invalid CIMD default scopes"):
        _validate_metadata(metadata)


@pytest.mark.parametrize(
    "metadata,error_match",
    [
        ([1, 2, 3], "JSON object"),
        (_metadata_factory(client_id="https://other.com/app"), "does not match"),
        (_metadata_factory(scope=["openid"]), "scope"),
        (_metadata_factory(scope=None), "scope"),
        (_metadata_factory(scope="openid unsupported"), "Unsupported scope"),
        (_metadata_factory(redirect_uris=[123]), "redirect_uris"),
        (_metadata_factory(redirect_uris=NotImplemented), "redirect_uris"),
        (
            _metadata_factory(post_logout_redirect_uris=[123]),
            "post_logout_redirect_uris",
        ),
        (
            _metadata_factory(
                post_logout_redirect_uris="https://app.example.com/logout"
            ),
            "post_logout_redirect_uris",
        ),
        (
            _metadata_factory(post_logout_redirect_uris=[]),
            "post_logout_redirect_uris",
        ),
    ],
)
def test_validate_metadata_invalid(db, metadata, error_match):
    with pytest.raises(ValidationError, match=error_match):
        _validate_metadata(metadata)


def test_fetch_success(response_mock, requests_get_mock):
    metadata = _metadata_factory()
    response_mock.iter_content.return_value = iter([json.dumps(metadata).encode()])
    result = cimd.fetch_metadata(CIMD_CLIENT_ID)
    assert result == metadata
    requests_get_mock.assert_called_once_with(
        CIMD_CLIENT_ID,
        timeout=cimd.FETCH_TIMEOUT,
        headers={"Accept": "application/json"},
        stream=True,
        allow_redirects=False,
    )


def test_fetch_non_200(response_mock):
    response_mock.status_code = HTTPStatus.NOT_FOUND
    with pytest.raises(ValidationError, match="404"):
        cimd.fetch_metadata(CIMD_CLIENT_ID)


def test_fetch_too_large_content_length(response_mock):
    response_mock.headers = {"Content-Length": "999999"}
    with pytest.raises(ValidationError, match="too large"):
        cimd.fetch_metadata(CIMD_CLIENT_ID)


@pytest.mark.parametrize(
    "body,error_match",
    [
        (b"x" * (cimd.MAX_RESPONSE_SIZE + 1), "too large"),
        (b"not json", "not valid JSON"),
    ],
)
def test_fetch_invalid_body(response_mock, body, error_match):
    response_mock.iter_content.return_value = iter([body])
    with pytest.raises(ValidationError, match=error_match):
        cimd.fetch_metadata(CIMD_CLIENT_ID)


def test_rate_limited(enable_cache, settings, request_context):
    settings.IDP_OIDC_RATE_LIMITS = {"cimd_fetch": "0/s/ip"}
    with pytest.raises(ValidationError, match="rate limited"):
        cimd.fetch_metadata_safely(CIMD_CLIENT_ID)


def test_thundering_herd_lock(enable_cache, request_context):
    lock_key = f"allauth.cimd.fetch:{CIMD_CLIENT_ID}"
    cache.add(lock_key, True, timeout=10)
    with pytest.raises(ValidationError, match="already in progress"):
        cimd.fetch_metadata_safely(CIMD_CLIENT_ID)


def test_lookup_non_cimd_returns_db_client(cimd_enabled, db):
    result = lookup_client("regular-client-id")
    assert result is None


def test_lookup_cimd_disabled(db, settings):
    settings.IDP_OIDC_CIMD_ENABLED = False
    result = lookup_client(CIMD_CLIENT_ID)
    assert result is None


def _mock_fetch(metadata=None):
    if metadata is None:
        metadata = _metadata_factory()
    return patch(
        "allauth.idp.oidc.internal.cimd.fetch_metadata_safely",
        return_value=metadata,
    )


def test_lookup_fresh_fetch(cimd_enabled, db, enable_cache, settings, request_context):
    with _mock_fetch():
        client = lookup_client(CIMD_CLIENT_ID)
    assert client is not None
    assert client.id == CIMD_CLIENT_ID
    assert client.type == Client.Type.PUBLIC
    assert Client.objects.filter(id=CIMD_CLIENT_ID).exists()


def test_lookup_cached_not_outdated(cimd_enabled, db, enable_cache, request_context):
    with _mock_fetch():
        client1 = lookup_client(CIMD_CLIENT_ID)

    with _mock_fetch() as mock_fetch:
        client2 = lookup_client(CIMD_CLIENT_ID)
        mock_fetch.assert_not_called()
    assert client2.id == client1.id


def test_lookup_outdated_refetches(
    cimd_enabled, db, enable_cache, settings, request_context
):
    settings.IDP_OIDC_CIMD_CACHE_TIMEOUT = 0
    with _mock_fetch():
        lookup_client(CIMD_CLIENT_ID)

    updated_metadata = _metadata_factory(client_name="Updated App")
    with _mock_fetch(updated_metadata):
        client = lookup_client(CIMD_CLIENT_ID)
    assert client.name == "Updated App"


def test_lookup_fetch_failure_returns_stale(
    cimd_enabled, db, enable_cache, settings, request_context
):
    with _mock_fetch():
        lookup_client(CIMD_CLIENT_ID)

    settings.IDP_OIDC_CIMD_CACHE_TIMEOUT = 0
    with patch(
        "allauth.idp.oidc.internal.cimd.fetch_metadata_safely",
        side_effect=requests.ConnectionError(),
    ):
        client = lookup_client(CIMD_CLIENT_ID)
    assert client is not None
    assert client.name == "Example App"


def test_lookup_fetch_failure_no_existing(
    cimd_enabled, db, enable_cache, request_context
):
    with patch(
        "allauth.idp.oidc.internal.cimd.fetch_metadata_safely",
        side_effect=ValidationError("fail"),
    ):
        client = lookup_client(CIMD_CLIENT_ID)
    assert client is None
