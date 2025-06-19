from unittest.mock import patch

from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.socialaccount.internal import flows
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.base.constants import AuthProcess


@pytest.mark.parametrize("reauthentication_required", [False, True])
def test_disconnect(auth_client, user, settings, mailoutbox, reauthentication_required):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = reauthentication_required
    account_to_del = SocialAccount.objects.create(
        uid="123", provider="other-server", user=user
    )
    account_to_keep = SocialAccount.objects.create(
        uid="456", provider="other-server", user=user
    )
    resp = auth_client.get(reverse("socialaccount_connections"))
    assertTemplateUsed(resp, "socialaccount/connections.html")
    resp = auth_client.post(
        reverse("socialaccount_connections"), {"account": account_to_del.pk}
    )
    if reauthentication_required:
        assert SocialAccount.objects.filter(pk=account_to_del.pk).exists()
        assert SocialAccount.objects.filter(pk=account_to_keep.pk).exists()
    else:
        assert not SocialAccount.objects.filter(pk=account_to_del.pk).exists()
        assert SocialAccount.objects.filter(pk=account_to_keep.pk).exists()
        assert len(mailoutbox) == 1
        assert mailoutbox[0].subject == "[example.com] Third-Party Account Disconnected"


def test_connect_with_reauthentication(
    auth_client, user, provider_callback_response, settings, user_password
):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = True
    resp = provider_callback_response(auth_client, process="connect")
    assert not SocialAccount.objects.filter(user=user).exists()
    assert resp.status_code == 302
    assert resp["location"] == reverse("account_reauthenticate")
    resp = auth_client.post(resp["location"], {"password": user_password})
    assert resp.status_code == 302
    assert resp["location"] == reverse("socialaccount_connections")
    assert SocialAccount.objects.filter(user=user).exists()


def test_connect(
    auth_client, user, provider_callback_response, settings, user_password, mailoutbox
):
    settings.ACCOUNT_EMAIL_NOTIFICATIONS = True
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = False
    resp = provider_callback_response(auth_client, process="connect")
    assert resp.status_code == 302
    assert SocialAccount.objects.filter(user=user).exists()
    assert resp["location"] == reverse("socialaccount_connections")
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "[example.com] Third-Party Account Connected"


@pytest.mark.parametrize(
    "email_authentication,account_exists, expected_action",
    [
        (False, False, "added"),
        (False, True, "updated"),
        (True, False, "added"),
        (True, True, "updated"),
    ],
)
def test_connect_vs_email_authentication(
    request_factory,
    sociallogin_factory,
    user,
    settings,
    email_authentication,
    account_exists,
    expected_action,
):
    settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION = email_authentication
    sociallogin = sociallogin_factory(email=user.email, provider="unittest-server")
    if account_exists:
        account = sociallogin.account
        account.user = user
        account.save()

    sociallogin.state["process"] = AuthProcess.CONNECT
    request = request_factory.get("/")
    request.user = user
    with patch(
        "allauth.account.adapter.DefaultAccountAdapter.add_message"
    ) as add_message:
        flows.login.complete_login(request, sociallogin)
        assert add_message.call_args[1]["message_context"]["action"] == expected_action
    assert SocialAccount.objects.filter(user=user, uid=sociallogin.account.uid).exists()
