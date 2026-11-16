import pytest

from tests.apps.socialaccount.base import setup_app


@pytest.fixture
def provider_id():
    return "oidc-server"


@pytest.fixture
def oidc_info():
    return {
        "authorization_endpoint": "/login",
        "userinfo_endpoint": "/userinfo",
        "token_endpoint": "/token",
        "jwks_uri": "/jwks",
        "issuer": "https://issuer.example.com",
        "end_session_endpoint": "https://issuer.example.com/logout",
    }


@pytest.fixture
def app(provider_id):
    app = setup_app(provider_id)
    app.provider_id = provider_id
    app.provider = "openid_connect"
    app.settings = {"server_url": "https://unittest.example.com"}
    app.save()
    return app
