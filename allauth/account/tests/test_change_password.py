from django.urls import reverse

import pytest


def test_change_unusable_password_redirects_to_set(client, user, user_password):
    user.set_unusable_password()
    user.save()
    client.force_login(user)
    resp = client.get(reverse("account_change_password"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_set_password")


def test_set_usable_password_redirects_to_change(auth_client, user):
    resp = auth_client.get(reverse("account_set_password"))
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_change_password")


@pytest.mark.parametrize(
    "logout,redirect_chain",
    [
        (
            False,
            [
                (reverse("account_change_password"), 302),
            ],
        ),
        (
            True,
            [
                (reverse("account_change_password"), 302),
                (
                    f'{reverse("account_login")}?next={reverse("account_change_password")}',
                    302,
                ),
            ],
        ),
    ],
)
def test_set_password(client, user, password_factory, logout, settings, redirect_chain):
    settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = logout
    user.set_unusable_password()
    user.save()
    client.force_login(user)
    password = password_factory()
    resp = client.post(
        reverse("account_set_password"),
        {"password1": password, "password2": password},
        follow=True,
    )
    assert resp.redirect_chain == redirect_chain


@pytest.mark.parametrize(
    "logout,redirect_chain",
    [
        (
            False,
            [
                (reverse("account_change_password"), 302),
            ],
        ),
        (
            True,
            [
                (reverse("account_change_password"), 302),
                (
                    f'{reverse("account_login")}?next={reverse("account_change_password")}',
                    302,
                ),
            ],
        ),
    ],
)
def test_change_password(
    auth_client,
    user,
    user_password,
    password_factory,
    logout,
    settings,
    redirect_chain,
    mailoutbox,
):
    settings.ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = logout
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    password = password_factory()
    resp = auth_client.post(
        reverse("account_change_password"),
        {"oldpassword": user_password, "password1": password, "password2": password},
        follow=True,
    )
    assert resp.redirect_chain == redirect_chain
    assert len(mailoutbox) == 1
    assert "Your password has been changed" in mailoutbox[0].body
