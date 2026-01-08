from http import HTTPStatus

from django.test.client import Client
from django.urls import reverse, reverse_lazy

import jwt
import pytest

from allauth.headless.tokens.strategies.jwt import JWTTokenStrategy


class CustomJWTTokenStrategy(JWTTokenStrategy):
    def get_claims(self, user):
        return {"email": user.email}


@pytest.fixture
def custom_jwt_token_strategy(settings):
    settings.HEADLESS_TOKEN_STRATEGY = (
        "tests.apps.headless.tokens.test_jwttokenstrategy.CustomJWTTokenStrategy"
    )


@pytest.fixture
def obtain_tokens(user, user_password, headless_reverse):
    def f(client):
        # Let's sign in
        resp = client.post(
            headless_reverse("headless:account:login"),
            data={
                "username": user.username,
                "password": user_password,
            },
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK

        # On sign in, we receive an access/refresh token pair.
        meta = resp.json()["meta"]
        assert meta["is_authenticated"]
        access_token = meta.get("access_token")
        refresh_token = meta.get("refresh_token")
        return access_token, refresh_token

    return f


@pytest.mark.parametrize("rotate", [False, True])
def test_rotate_refresh_token(
    headless_client,
    headless_reverse,
    client,
    user,
    rotate,
    settings,
    obtain_tokens,
    custom_jwt_token_strategy,
):
    if headless_client == "browser":
        return
    settings.HEADLESS_JWT_ROTATE_REFRESH_TOKEN = rotate

    access_token, refresh_token = obtain_tokens(client)

    # Check our custom claim
    access_token_data = jwt.decode(
        access_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    assert access_token_data["email"] == user.email

    # Let's refresh
    resp = Client().post(
        headless_reverse("headless:tokens:refresh"),
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()["data"]

    # Check our custom claim in the new access token
    access_token = data["access_token"]
    access_token_data = jwt.decode(
        access_token, algorithms=["RS256"], options={"verify_signature": False}
    )
    assert access_token_data["email"] == user.email

    new_refresh_token = data.get("refresh_token")
    assert bool(new_refresh_token) == rotate

    # Let's refresh, again using the previous refresh token
    resp = Client().post(
        headless_reverse("headless:tokens:refresh"),
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )
    assert resp.status_code == (HTTPStatus.BAD_REQUEST if rotate else HTTPStatus.OK)

    # Let's refresh, using the new refresh token
    if new_refresh_token:
        resp = Client().post(
            headless_reverse("headless:tokens:refresh"),
            data={"refresh_token": new_refresh_token},
            content_type="application/json",
        )
        assert resp.status_code == HTTPStatus.OK


@pytest.mark.parametrize("stateful_validation_enabled", [False, True])
def test_flow(
    headless_client,
    headless_reverse,
    client,
    user,
    settings,
    stateful_validation_enabled,
    obtain_tokens,
):
    settings.HEADLESS_JWT_ROTATE_REFRESH_TOKEN = False
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = stateful_validation_enabled

    access_token, refresh_token = obtain_tokens(client)

    # On sign in, we receive an access/refresh token pair.
    if headless_client == "browser":
        assert not access_token
        assert not refresh_token
        return

    # With the access token, we can reach out to the allauth API.
    at_client = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    resp = at_client.get(headless_reverse("headless:account:current_session"))
    assert resp.status_code == HTTPStatus.OK

    # Also check validity with DRF & Ninja endpoints
    for url in [
        reverse("headless_rest_framework_resource"),
        "/headless/ninja/resource",
    ]:
        resp = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}").get(
            f"{url}?userinfo"
        )
        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"resource": "ok", "user_email": user.email}

    # With the refresh token, we can retrieve a new access token.
    resp = Client().post(
        headless_reverse("headless:tokens:refresh"),
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    new_access_token = resp.json()["data"]["access_token"]
    assert new_access_token != access_token

    # And, of course, that new access token is valid.
    at_client = Client(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
    resp = at_client.get(headless_reverse("headless:account:current_session"))
    assert resp.status_code == HTTPStatus.OK

    # Also check validity with DRF & Ninja endpoints
    for url in [
        reverse("headless_rest_framework_resource"),
        "/headless/ninja/resource",
    ]:
        resp = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}").get(
            f"{url}?userinfo"
        )
        assert resp.status_code == HTTPStatus.OK
        assert resp.json() == {"resource": "ok", "user_email": user.email}

    # But, when we logout...
    resp = at_client.delete(headless_reverse("headless:account:current_session"))
    assert resp.status_code == HTTPStatus.UNAUTHORIZED

    # ... the refresh token no longer works.
    resp = Client().post(
        headless_reverse("headless:tokens:refresh"),
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # And, the access token no longer functions...
    at_client = Client(HTTP_AUTHORIZATION=f"Bearer {new_access_token}")
    resp = at_client.get(headless_reverse("headless:account:current_session"))
    assert resp.status_code == (
        HTTPStatus.UNAUTHORIZED if stateful_validation_enabled else HTTPStatus.GONE
    )

    # Also check validity with DRF & Ninja endpoints
    for url in [
        reverse("headless_rest_framework_resource"),
        "/headless/ninja/resource",
    ]:
        resp = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}").get(url)
        assert resp.status_code == (
            HTTPStatus.UNAUTHORIZED if stateful_validation_enabled else HTTPStatus.OK
        )


@pytest.mark.parametrize("stateful,query_count", [(False, 0), (True, 1)])
@pytest.mark.parametrize(
    "url",
    [
        reverse_lazy("headless_rest_framework_resource"),
        "/headless/ninja/resource",
    ],
)
def test_access_token_query_counts(
    headless_client,
    headless_reverse,
    client,
    settings,
    obtain_tokens,
    django_assert_num_queries,
    stateful,
    query_count,
    url,
):
    if headless_client == "browser":
        return
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )
    settings.HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED = stateful
    access_token, _ = obtain_tokens(client)
    with django_assert_num_queries(query_count):
        resp = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}").get(url)
        assert resp.status_code == (HTTPStatus.OK)


@pytest.mark.parametrize("settings_scheme", ["Bearer", "Token", "JWT"])
@pytest.mark.parametrize("request_scheme", ["Bearer", "Token", "JWT"])
def test_custom_authorization_header_scheme(
    headless_client,
    headless_reverse,
    client,
    settings,
    obtain_tokens,
    settings_scheme,
    request_scheme,
):
    """Test that JWT_AUTHORIZATION_HEADER_SCHEME setting is respected."""
    if headless_client == "browser":
        return

    # Set authorization header scheme in settings
    settings.HEADLESS_JWT_AUTHORIZATION_HEADER_SCHEME = settings_scheme
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )

    access_token, _ = obtain_tokens(client)

    # Make request with the specified scheme
    at_client = Client(HTTP_AUTHORIZATION=f"{request_scheme} {access_token}")
    resp = at_client.get(headless_reverse("headless:account:current_session"))

    # Should succeed only when request scheme matches settings scheme
    if settings_scheme == request_scheme:
        assert resp.status_code == HTTPStatus.OK
    else:
        assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_hs256_algorithm(
    headless_client,
    headless_reverse,
    client,
    settings,
    user,
    obtain_tokens,
):
    if headless_client == "browser":
        return
    settings.HEADLESS_JWT_ALGORITHM = "HS256"
    settings.HEADLESS_JWT_PRIVATE_KEY = "super-secret"
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )

    access_token, _ = obtain_tokens(client)

    header = jwt.get_unverified_header(access_token)
    assert header["alg"] == "HS256"
    assert "kid" not in header

    payload = jwt.decode(
        access_token,
        key="super-secret",
        algorithms=["HS256"],
        options={"verify_signature": True, "verify_iss": False, "verify_aud": False},
    )
    assert payload["sub"] == str(user.pk)

    at_client = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    resp = at_client.get(headless_reverse("headless:account:current_session"))
    assert resp.status_code == HTTPStatus.OK


def test_hs256_fallback_to_secret_key(
    headless_client,
    headless_reverse,
    client,
    settings,
    user,
    obtain_tokens,
):
    if headless_client == "browser":
        return
    settings.HEADLESS_JWT_ALGORITHM = "HS256"
    settings.HEADLESS_JWT_PRIVATE_KEY = ""  # Empty
    settings.SECRET_KEY = "django-secret-fallback"
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )

    access_token, _ = obtain_tokens(client)

    payload = jwt.decode(
        access_token,
        key="django-secret-fallback",
        algorithms=["HS256"],
        options={"verify_signature": True, "verify_iss": False, "verify_aud": False},
    )
    assert payload["sub"] == str(user.pk)
