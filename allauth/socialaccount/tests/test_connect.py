from django.urls import reverse

from pytest_django.asserts import assertTemplateUsed

from allauth.socialaccount.models import SocialAccount


def test_disconnect(auth_client, user):
    account = SocialAccount.objects.create(uid="123", provider="twitter", user=user)
    resp = auth_client.get(reverse("socialaccount_connections"))
    assertTemplateUsed(resp, "socialaccount/connections.html")
    resp = auth_client.post(
        reverse("socialaccount_connections"), {"account": account.pk}
    )
    assert not SocialAccount.objects.filter(pk=account.pk).exists()


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
    auth_client, user, provider_callback_response, settings, user_password
):
    settings.ACCOUNT_REAUTHENTICATION_REQUIRED = False
    resp = provider_callback_response(auth_client, process="connect")
    assert resp.status_code == 302
    assert SocialAccount.objects.filter(user=user).exists()
    assert resp["location"] == reverse("socialaccount_connections")
