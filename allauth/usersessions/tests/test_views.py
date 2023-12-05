from django.test import Client
from django.urls import reverse

from allauth.usersessions.models import UserSession


def test_overall_flow(user, user_password):
    firefox = Client(HTTP_USER_AGENT="Mozilla Firefox")
    nyxt = Client(HTTP_USER_AGENT="Nyxt")
    for client in [firefox, nyxt]:
        resp = client.post(
            reverse("account_login"),
            {"login": user.username, "password": user_password},
        )
        assert resp.status_code == 302
    assert UserSession.objects.filter(user=user).count() == 2
    sessions = list(UserSession.objects.filter(user=user).order_by("pk"))
    assert sessions[0].user_agent == "Mozilla Firefox"
    assert sessions[1].user_agent == "Nyxt"
    for client in [firefox, nyxt]:
        resp = firefox.get(reverse("usersessions_list"))
        assert resp.status_code == 200
    resp = firefox.post(reverse("usersessions_list"))
    assert resp.status_code == 302
    assert UserSession.objects.filter(user=user).count() == 1
    assert UserSession.objects.filter(user=user, pk=sessions[0].pk).exists()
    assert not UserSession.objects.filter(user=user, pk=sessions[1].pk).exists()
    resp = nyxt.get(reverse("usersessions_list"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_login") + "?next=" + reverse(
        "usersessions_list"
    )
