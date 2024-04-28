from allauth.usersessions.models import UserSession


def test_flow(client, user, user_password, headless_reverse, settings):
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    resp = client.post(
        headless_reverse("headless:account:login"),
        data={
            "email": user.email,
            "password": user_password,
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    resp = client.get(headless_reverse("headless:usersessions:sessions"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 1
    session_pk = data["data"][0]["id"]
    assert UserSession.objects.filter(pk=session_pk).exists()
    resp = client.delete(
        headless_reverse("headless:usersessions:sessions"),
        data={"sessions": [session_pk]},
        content_type="application/json",
    )
    assert resp.status_code == 401
    assert not UserSession.objects.filter(pk=session_pk).exists()
