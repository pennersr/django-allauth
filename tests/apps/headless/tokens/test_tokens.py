from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from allauth.headless.tokens.strategies.sessions import SessionTokenStrategy


class DummyAccessTokenStrategy(SessionTokenStrategy):
    def create_access_token(self, request):
        return f"at-user-{request.user.pk}"


def external_auth_middleware(get_response):
    def middleware(request):
        user_pk = request.headers.get("x-external-user")
        if user_pk:
            request.user = get_user_model().objects.get(pk=user_pk)
        return get_response(request)

    return middleware


def test_refresh_with_stale_session_token_while_externally_authenticated(
    app_client,
    user,
    settings,
):
    settings.MIDDLEWARE = list(settings.MIDDLEWARE) + [
        "tests.apps.headless.tokens.test_tokens.external_auth_middleware"
    ]
    app_client.session_token = "stale-session-token"
    resp = app_client.post(
        reverse("headless:app:tokens:refresh"),
        data={"refresh_token": "irrelevant"},
        content_type="application/json",
        HTTP_X_EXTERNAL_USER=str(user.pk),
    )
    assert resp.status_code == HTTPStatus.GONE
    assert resp.json()["meta"]["is_authenticated"] is None


def test_access_token(
    client,
    user,
    user_password,
    settings,
    headless_reverse,
    headless_client,
):
    settings.HEADLESS_TOKEN_STRATEGY = (
        "tests.apps.headless.tokens.test_tokens.DummyAccessTokenStrategy"
    )
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "username": user.username,
            "password": user_password,
        },
        content_type="application/json",
    )
    data = resp.json()
    assert data["status"] == HTTPStatus.OK
    if headless_client == "app":
        assert data["meta"]["access_token"] == f"at-user-{user.pk}"
    else:
        assert "access_token" not in data["meta"]
