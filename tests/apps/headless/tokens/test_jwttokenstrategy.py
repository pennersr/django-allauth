from http import HTTPStatus

from django.test.client import Client
from django.urls import reverse, reverse_lazy

import pytest


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
    headless_client, headless_reverse, client, rotate, settings, obtain_tokens
):
    if headless_client == "browser":
        return
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
    )
    settings.HEADLESS_JWT_ROTATE_REFRESH_TOKEN = rotate

    _, refresh_token = obtain_tokens(client)

    # Let's refresh
    resp = Client().post(
        headless_reverse("headless:tokens:refresh"),
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()["data"]

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
            url + "?userinfo"
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
            url + "?userinfo"
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
