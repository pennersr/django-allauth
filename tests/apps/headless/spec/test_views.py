from http import HTTPStatus
from pathlib import Path

from django import forms
from django.urls import reverse

import yaml

from allauth.headless.spec.internal import schema
from allauth.headless.tokens.strategies.sessions import SessionTokenStrategy


CUSTOM_TOKEN_SPEC = {
    "securitySchemes": {
        "CustomToken": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Custom-Token",
        }
    },
    "security": [{"CustomToken": []}, {}],
}


class CustomTokenStrategy(SessionTokenStrategy):
    @classmethod
    def openapi_spec(cls):
        return CUSTOM_TOKEN_SPEC


def test_openapi_source_uses_session_token_security():
    path = Path(schema.__file__).parent.parent / "doc/openapi.yaml"
    with path.open("rb") as fp:
        source = yaml.safe_load(fp)

    session_token_spec = SessionTokenStrategy.openapi_spec()
    assert (
        source["components"]["securitySchemes"] == session_token_spec["securitySchemes"]
    )
    assert _auth_security(source) == session_token_spec["security"]


def test_openapi_json(client):
    resp = client.get(reverse("headless:openapi_json"))
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["openapi"] == "3.0.3"
    assert data["info"]["description"].startswith("# Introduction")
    assert "AuthToken" not in data["components"]["parameters"]
    assert data["components"]["securitySchemes"] == {
        "SessionToken": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Session-Token",
            "description": "Session token. Only needed when `client` is equal to `app`.",
        }
    }
    assert _auth_security(data) == [{"SessionToken": []}, {}]


def test_openapi_json_with_custom_token_strategy(settings, client):
    settings.HEADLESS_TOKEN_STRATEGY = (
        "tests.apps.headless.spec.test_views.CustomTokenStrategy"
    )

    resp = client.get(reverse("headless:openapi_json"))

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert "AuthToken" not in data["components"]["parameters"]
    assert data["components"]["securitySchemes"] == CUSTOM_TOKEN_SPEC["securitySchemes"]
    assert _auth_security(data) == CUSTOM_TOKEN_SPEC["security"]


def test_openapi_json_with_jwt_token_strategy(settings, client):
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )

    resp = client.get(reverse("headless:openapi_json"))

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert "AuthToken" not in data["components"]["parameters"]
    assert data["components"]["securitySchemes"] == {
        "SessionToken": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Session-Token",
            "description": "Session token. Only needed when `client` is equal to `app`.",
        },
        "JWT": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "JWT access token, using the `Bearer` authorization scheme. "
                "Only needed when `client` is equal to `app`."
            ),
        },
    }
    assert _auth_security(data) == [{"SessionToken": []}, {"JWT": []}, {}]


def test_openapi_json_with_custom_jwt_authorization_scheme(settings, client):
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )
    settings.HEADLESS_JWT_AUTHORIZATION_HEADER_SCHEME = "Token"

    resp = client.get(reverse("headless:openapi_json"))

    assert resp.status_code == HTTPStatus.OK
    assert resp.json()["components"]["securitySchemes"]["JWT"] == {
        "type": "http",
        "scheme": "token",
        "description": (
            "JWT access token, using the `Token` authorization scheme. "
            "Only needed when `client` is equal to `app`."
        ),
    }


def _auth_security(spec):
    security = [
        operation["security"]
        for path_spec in spec["paths"].values()
        for operation in path_spec.values()
        if isinstance(operation, dict) and "security" in operation
    ]
    assert security
    assert all(value == security[0] for value in security)
    return security[0]


class SpecCustomSignupForm(forms.Form):
    favorite_color = forms.ChoiceField(choices=[("red", "Red"), ("blue", "Blue")])
    hobbies = forms.MultipleChoiceField(
        choices=[("chess", "Chess"), ("poker", "Poker")],
        required=True,
        help_text="Pick your hobbies.",
    )
    nickname = forms.CharField(min_length=2, max_length=30, help_text="Your nickname.")
    age = forms.IntegerField()
    rating = forms.FloatField()
    newsletter = forms.BooleanField()
    birth_date = forms.DateField()
    signed_up_at = forms.DateTimeField()
    contact_email = forms.EmailField()
    website = forms.URLField()
    balance = forms.DecimalField()

    def signup(self, request, user):
        pass


def test_openapi_json_with_custom_signup_form(settings, client):
    settings.ACCOUNT_SIGNUP_FORM_CLASS = (
        "tests.apps.headless.spec.test_views.SpecCustomSignupForm"
    )
    resp = client.get(reverse("headless:openapi_json"))
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    base_signup = data["components"]["schemas"]["BaseSignup"]
    assert base_signup["properties"]["favorite_color"] == {
        "type": "string",
        "enum": ["red", "blue"],
    }
    assert base_signup["properties"]["hobbies"] == {
        "type": "array",
        "items": {"type": "string", "enum": ["chess", "poker"]},
        "description": "Pick your hobbies.",
    }
    assert base_signup["properties"]["nickname"] == {
        "type": "string",
        "maxLength": 30,
        "minLength": 2,
        "description": "Your nickname.",
    }
    assert base_signup["properties"]["age"] == {"type": "integer"}
    assert base_signup["properties"]["rating"] == {"type": "number"}
    assert base_signup["properties"]["newsletter"] == {"type": "boolean"}
    assert base_signup["properties"]["birth_date"] == {
        "type": "string",
        "format": "date",
    }
    assert base_signup["properties"]["signed_up_at"] == {
        "type": "string",
        "format": "date-time",
    }
    assert base_signup["properties"]["contact_email"] == {
        "type": "string",
        "format": "email",
        "maxLength": 320,
    }
    assert base_signup["properties"]["website"] == {
        "type": "string",
        "format": "uri",
    }
    assert base_signup["properties"]["balance"] == {
        "type": "string",
        "format": "decimal",
        "pattern": r"^\d+(\.\d+)?$",
    }
    assert "hobbies" in base_signup["required"]
