import json
from http import HTTPStatus

from django.urls import reverse

import pytest

from allauth.idp.oidc.models import Client


@pytest.fixture
def dcr_settings(settings_impacting_urls):
    """Enable DCR for the duration of a test."""

    def f(**overrides):
        kv = {"IDP_OIDC_DCR_ENABLED": True}
        kv.update(overrides)
        return settings_impacting_urls(**kv)

    return f


def _register(client, data):
    return client.post(
        reverse("idp:oidc:client_registration"),
        data=json.dumps(data),
        content_type="application/json",
    )


def test_register_public_client(client, dcr_settings, db):
    """Should register a public client with PKCE (no secret)."""
    with dcr_settings():
        resp = _register(
            client,
            {
                "client_name": "ChatGPT",
                "redirect_uris": ["https://chatgpt.com/callback"],
                "grant_types": ["authorization_code"],
                "response_types": ["code"],
                "token_endpoint_auth_method": "none",
                "scope": "openid profile",
            },
        )
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert data["client_name"] == "ChatGPT"
    assert data["redirect_uris"] == ["https://chatgpt.com/callback"]
    assert data["grant_types"] == ["authorization_code"]
    assert data["response_types"] == ["code"]
    assert data["token_endpoint_auth_method"] == "none"
    assert data["scope"] == "openid profile"
    assert "client_id" in data
    assert "client_secret" not in data
    assert "client_id_issued_at" in data

    # Verify client was persisted.
    db_client = Client.objects.get(id=data["client_id"])
    assert db_client.type == Client.Type.PUBLIC
    assert db_client.get_scopes() == ["openid", "profile"]
    assert db_client.get_redirect_uris() == ["https://chatgpt.com/callback"]


def test_register_confidential_client(client, dcr_settings, db):
    """Should register a confidential client and return a secret."""
    with dcr_settings():
        resp = _register(
            client,
            {
                "client_name": "My Server",
                "redirect_uris": ["https://example.com/callback"],
                "token_endpoint_auth_method": "client_secret_basic",
            },
        )
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert "client_secret" in data
    assert data["client_secret_expires_at"] == 0

    db_client = Client.objects.get(id=data["client_id"])
    assert db_client.type == Client.Type.CONFIDENTIAL
    assert db_client.check_secret(data["client_secret"])


def test_register_missing_redirect_uris(client, dcr_settings, db):
    """Should reject registration without redirect_uris."""
    with dcr_settings():
        resp = _register(client, {"client_name": "Bad Client"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["error"] == "invalid_redirect_uri"


def test_register_invalid_json(client, dcr_settings, db):
    """Should reject malformed JSON body."""
    with dcr_settings():
        resp = client.post(
            reverse("idp:oidc:client_registration"),
            data="not json",
            content_type="application/json",
        )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["error"] == "invalid_client_metadata"


def test_register_default_scopes(client, dcr_settings, db):
    """Should default to openid scope when none specified."""
    with dcr_settings():
        resp = _register(
            client,
            {
                "redirect_uris": ["https://example.com/callback"],
                "token_endpoint_auth_method": "none",
            },
        )
    assert resp.status_code == HTTPStatus.CREATED
    assert resp.json()["scope"] == "openid"


def test_register_default_auth_method(client, dcr_settings, db):
    """Should default to public client (auth method 'none')."""
    with dcr_settings():
        resp = _register(
            client,
            {"redirect_uris": ["https://example.com/callback"]},
        )
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert data["token_endpoint_auth_method"] == "none"
    assert "client_secret" not in data


def test_dcr_disabled_by_default(client, db):
    """Should 404 when DCR is not enabled."""
    with pytest.raises(Exception):
        # URL doesn't exist when DCR is disabled.
        reverse("idp:oidc:client_registration")


def test_configuration_includes_registration_endpoint(
    client, dcr_settings, oidc_client
):
    """Should advertise registration_endpoint in OIDC configuration when DCR is enabled."""
    with dcr_settings():
        resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert "registration_endpoint" in data
    assert data["registration_endpoint"].endswith("/identity/o/api/register")


def test_configuration_excludes_registration_when_disabled(client, oidc_client):
    """Should not include registration_endpoint when DCR is disabled."""
    resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert "registration_endpoint" not in data


def test_configuration_includes_pkce(client, oidc_client):
    """Should always advertise PKCE (S256) support."""
    resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert data["code_challenge_methods_supported"] == ["S256"]


def test_configuration_includes_grant_types(client, oidc_client):
    """Should advertise supported grant types."""
    resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert "grant_types_supported" in data
    assert "authorization_code" in data["grant_types_supported"]


def test_configuration_includes_token_auth_methods(client, oidc_client):
    """Should advertise token endpoint auth methods."""
    resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert data["token_endpoint_auth_methods_supported"] == [
        "none",
        "client_secret_basic",
        "client_secret_post",
    ]


def test_register_adapter_validation(client, dcr_settings, db, settings):
    """Should reject registration when adapter validation raises."""
    settings.IDP_OIDC_ADAPTER = (
        "tests.apps.idp.oidc.test_dcr.RejectingAdapter"
    )
    with dcr_settings():
        resp = _register(
            client,
            {
                "redirect_uris": ["https://example.com/callback"],
                "token_endpoint_auth_method": "none",
            },
        )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json()["error"] == "invalid_client_metadata"
    assert "rejected" in resp.json()["error_description"].lower()


class RejectingAdapter:
    """Test adapter that rejects all DCR requests."""

    def validate_client_registration(self, registration_data):
        from django.core.exceptions import ValidationError

        raise ValidationError("Registration rejected by policy.")

    def __getattr__(self, name):
        from allauth.idp.oidc.adapter import DefaultOIDCAdapter

        return getattr(DefaultOIDCAdapter(), name)
