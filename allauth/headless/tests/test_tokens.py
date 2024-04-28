from allauth.headless.tokens.sessions import SessionTokenStrategy


class DummyAccessTokenStrategy(SessionTokenStrategy):
    def create_access_token(self, request):
        return f"at-user-{request.user.pk}"


def test_access_token(
    client,
    user,
    user_password,
    settings,
    headless_reverse,
    headless_client,
):
    settings.HEADLESS_TOKEN_STRATEGY = (
        "allauth.headless.tests.test_tokens.DummyAccessTokenStrategy"
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
    assert data["status"] == 200
    if headless_client == "app":
        assert data["meta"]["access_token"] == f"at-user-{user.pk}"
    else:
        assert "access_token" not in data["meta"]
