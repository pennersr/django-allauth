from django.test import Client
from django.urls import reverse

import pytest

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


@pytest.mark.parametrize("logout_on_passwd_change", [True, False])
def test_change_password_updates_user_session(
    settings, logout_on_passwd_change, client, user, user_password, password_factory
):
    settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = logout_on_passwd_change
    resp = client.post(
        reverse("account_login"),
        {"login": user.username, "password": user_password},
    )
    assert resp.status_code == 302
    assert len(UserSession.objects.purge_and_list(user)) == 1

    new_password = password_factory()
    resp = client.post(
        reverse("account_change_password"),
        {
            "oldpassword": user_password,
            "password1": new_password,
            "password2": new_password,
        },
    )
    assert len(UserSession.objects.purge_and_list(user)) == (
        0 if logout_on_passwd_change else 1
    )
