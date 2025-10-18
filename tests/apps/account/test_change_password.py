from http import HTTPStatus

from django.urls import reverse, reverse_lazy

import pytest


def test_change_unusable_password_redirects_to_set(client, user, user_password):
    user.set_unusable_password()
    user.save()
    client.force_login(user)
    resp = client.get(reverse("account_change_password"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_set_password")


def test_set_usable_password_redirects_to_change(auth_client, user):
    resp = auth_client.get(reverse("account_set_password"))
    assert resp.status_code == HTTPStatus.FOUND
    assert resp["location"] == reverse("account_change_password")


@pytest.mark.parametrize(
    "logout,next_url,redirect_chain",
    [
        (False, "", [(reverse_lazy("account_change_password"), HTTPStatus.FOUND)]),
        (False, "/foo", [("/foo", HTTPStatus.FOUND)]),
        (
            True,
            "",
            [
                (reverse_lazy("account_change_password"), HTTPStatus.FOUND),
                (
                    "/accounts/login/?next=/accounts/password/change/",
                    HTTPStatus.FOUND,
                ),
            ],
        ),
        (True, "/foo", [("/foo", HTTPStatus.FOUND)]),
    ],
)
def test_set_password(
    client, user, next_url, password_factory, logout, settings, redirect_chain
):
    settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = logout
    user.set_unusable_password()
    user.save()
    client.force_login(user)
    password = password_factory()
    data = {"password1": password, "password2": password}
    if next_url:
        data["next"] = next_url
    resp = client.post(
        reverse("account_set_password"),
        data,
        follow=True,
    )
    assert resp.redirect_chain == redirect_chain


@pytest.mark.parametrize(
    "logout,next_url,redirect_chain",
    [
        (False, "", [(reverse_lazy("account_change_password"), HTTPStatus.FOUND)]),
        (False, "/foo", [("/foo", HTTPStatus.FOUND)]),
        (
            True,
            "",
            [
                (reverse_lazy("account_change_password"), HTTPStatus.FOUND),
                (
                    "/accounts/login/?next=/accounts/password/change/",
                    HTTPStatus.FOUND,
                ),
            ],
        ),
        (True, "/foo", [("/foo", HTTPStatus.FOUND)]),
    ],
)
def test_change_password(
    auth_client,
    user,
    user_password,
    next_url,
    password_factory,
    logout,
    settings,
    redirect_chain,
    mailoutbox,
):
    settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = logout
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    password = password_factory()
    data = {"oldpassword": user_password, "password1": password, "password2": password}
    if next_url:
        data["next"] = next_url
    resp = auth_client.post(
        reverse("account_change_password"),
        data,
        follow=True,
    )
    assert resp.redirect_chain == redirect_chain
    assert len(mailoutbox) == 1
    assert "Your password has been changed" in mailoutbox[0].body
