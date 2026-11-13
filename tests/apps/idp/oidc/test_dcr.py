import json
from http import HTTPStatus
from typing import Any
from unittest.mock import ANY

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse

import pytest

from allauth.core.exceptions import ImmediateHttpResponse
from allauth.idp.oidc.adapter import DefaultOIDCAdapter
from allauth.idp.oidc.models import Client, Token


class DCRTestAdapter(DefaultOIDCAdapter):
    def validate_client_registration(self, *, client_metadata, **kwargs):
        name = client_metadata.get("client_name")
        if name == "Validation Error":
            raise ValidationError("Custom validation error.")
        elif name == "Immediate Response":
            raise ImmediateHttpResponse(
                JsonResponse(
                    status=HTTPStatus.GONE,
                    data={"error": "custom", "error_description": "Custom."},
                )
            )


@pytest.fixture
def initial_access_token_required():
    return False


@pytest.fixture
def dcr_enabled(settings_impacting_urls, initial_access_token_required):
    with settings_impacting_urls(
        IDP_OIDC_DCR_ENABLED=True,
        IDP_OIDC_DCR_REQUIRES_INITIAL_ACCESS_TOKEN=initial_access_token_required,
        IDP_OIDC_ADAPTER=("tests.apps.idp.oidc.test_dcr.DCRTestAdapter"),
    ):
        yield


@pytest.fixture
def register_client(client, dcr_enabled, db):
    def register(data: Any, authorization: str | None = None):
        kwargs = {}
        if authorization is not None:
            kwargs["HTTP_AUTHORIZATION"] = authorization
        return client.post(
            reverse("idp:oidc:client_registration"),
            data=json.dumps(data),
            content_type="application/json",
            **kwargs,
        )

    return register


def test_public_client(register_client):
    client_metadata = {
        "client_name": "Dynamic Client",
        "redirect_uris": ["https://dynaclient.org/callback"],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "logo_uri": "https://client.example.org/logo.png",
        "scope": "openid profile",
    }
    resp = register_client(client_metadata)
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert data == {
        "client_id": ANY,
        "client_id_issued_at": ANY,
        "client_name": "Dynamic Client",
        "redirect_uris": ["https://dynaclient.org/callback"],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "scope": "openid profile",
    }
    client = Client.objects.get(id=data["client_id"])
    assert client.type == Client.Type.PUBLIC
    assert client.get_scopes() == ["openid", "profile"]
    assert client.get_redirect_uris() == ["https://dynaclient.org/callback"]
    assert client.data["dcr"]
    assert client.data["client_metadata"] == client_metadata


def test_confidential_client(register_client):
    resp = register_client(
        {
            "client_name": "My Server",
            "redirect_uris": ["https://example.com/callback"],
            "post_logout_redirect_uris": ["https://example.com/logout"],
            "token_endpoint_auth_method": "client_secret_basic",
        },
    )
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert "client_secret" in data
    assert data["client_secret_expires_at"] == 0

    client = Client.objects.get(id=data["client_id"])
    assert client.type == Client.Type.CONFIDENTIAL
    assert client.check_secret(data["client_secret"])
    assert client.get_post_logout_redirect_uris() == ["https://example.com/logout"]


def test_missing_redirect_uris(register_client):
    resp = register_client({"client_name": "Client without redirect URIs"})
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_redirect_uri",
        "error_description": "'redirect_uris': This field is required.",
    }


def test_invalid_post_logout_redirect_uris(register_client):
    resp = register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
            "post_logout_redirect_uris": ["https://example.com/logout", 123],
        }
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_client_metadata",
        "error_description": (
            "'post_logout_redirect_uris': post_logout_redirect_uris must be an"
            " array of strings."
        ),
    }


def test_invalid_json_value(register_client):
    resp = register_client(666)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_client_metadata",
        "error_description": "Invalid JSON data.",
    }


def test_invalid_content_type(client, dcr_enabled, db):
    resp = client.post(
        reverse("idp:oidc:client_registration"),
        data="not JSON",
        content_type="text/plain",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_client_metadata",
        "error_description": "Invalid JSON data.",
    }


def test_default_scopes(register_client):
    resp = register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
        },
    )
    assert resp.status_code == HTTPStatus.CREATED
    assert resp.json()["scope"] == "openid profile email"


def test_configured_default_scopes(register_client, settings):
    settings.IDP_OIDC_SCOPE_CHOICES = [
        "openid",
        ("mcp", "Use the MCP server"),
    ]
    settings.IDP_OIDC_DCR_DEFAULT_SCOPES = ["openid", "mcp"]
    resp = register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
        },
    )
    assert resp.status_code == HTTPStatus.CREATED
    assert resp.json()["scope"] == "openid mcp"


def test_unsupported_scope(register_client):
    resp = register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
            "scope": "openid unsupported",
        },
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.json() == {
        "error": "invalid_client_metadata",
        "error_description": "'scope': Unsupported scope(s): unsupported",
    }


def test_default_auth_method(register_client):
    resp = register_client(
        {"redirect_uris": ["https://example.com/callback"]},
    )
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert data["token_endpoint_auth_method"] == "client_secret_basic"
    assert "client_secret" in data


def test_dcr_disabled_by_default():
    with pytest.raises(NoReverseMatch):
        reverse("idp:oidc:client_registration")


def test_configuration_includes_registration_endpoint(client, dcr_enabled, db):
    resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert "registration_endpoint" in data
    assert data["registration_endpoint"].endswith(
        reverse("idp:oidc:client_registration")
    )


def test_configuration_excludes_registration_when_disabled(client, db):
    resp = client.get(reverse("idp:oidc:configuration"))
    data = resp.json()
    assert "registration_endpoint" not in data


def test_rate_limits(register_client, enable_cache, settings):
    settings.IDP_OIDC_RATE_LIMITS = {"client_registration": "2/m/ip"}
    for attempt in range(3):
        resp = register_client(
            {
                "redirect_uris": ["https://example.com/callback"],
            }
        )
        assert resp.status_code == (
            HTTPStatus.CREATED if attempt <= 1 else HTTPStatus.TOO_MANY_REQUESTS
        )


@pytest.mark.parametrize(
    "client_name,status,result",
    [
        (
            "Validation Error",
            HTTPStatus.BAD_REQUEST,
            {
                "error": "invalid_client_metadata",
                "error_description": "Custom validation error.",
            },
        ),
        (
            "Immediate Response",
            HTTPStatus.GONE,
            {
                "error": "custom",
                "error_description": "Custom.",
            },
        ),
        (
            "Too long" * 100,
            HTTPStatus.BAD_REQUEST,
            {
                "error": "invalid_client_metadata",
                "error_description": "'client_name': Ensure this value has at most 100 characters (it has 800).",
            },
        ),
        (
            "<script>alert(1)</script>",
            HTTPStatus.BAD_REQUEST,
            {
                "error": "invalid_client_metadata",
                "error_description": "'client_name': Client name must not contain '<' or '>'.",
            },
        ),
    ],
)
def test_validation_errors(register_client, client_name, result, status):
    resp = register_client(
        {
            "client_name": client_name,
            "redirect_uris": ["https://example.com/callback"],
        },
    )
    assert resp.status_code == status
    assert resp.json() == result


@pytest.mark.parametrize("initial_access_token_required", (True,))
@pytest.mark.parametrize(
    "authorization_method,authorization_token,token_type,status",
    [
        (None, None, None, HTTPStatus.UNAUTHORIZED),
        ("Bearer", "iat", Token.Type.INITIAL_ACCESS_TOKEN, HTTPStatus.CREATED),
        ("Bearer", "at", Token.Type.ACCESS_TOKEN, HTTPStatus.UNAUTHORIZED),
        ("BeArEr", "iat", Token.Type.INITIAL_ACCESS_TOKEN, HTTPStatus.CREATED),
        ("Token", "iat", Token.Type.INITIAL_ACCESS_TOKEN, HTTPStatus.UNAUTHORIZED),
    ],
)
def test_authorization(
    initial_access_token_required,
    register_client,
    authorization_method,
    authorization_token,
    token_type,
    status,
):
    authorization = None
    if authorization_method:
        authorization = f"{authorization_method} {authorization_token}"
    if token_type:
        token = Token(type=token_type)
        token.set_value(authorization_token)
        token.save()
    resp = register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
        },
        authorization=authorization,
    )
    assert resp.status_code == status
