import copy
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.core import context
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount


@pytest.mark.parametrize("with_emailaddress", [False, True])
@pytest.mark.parametrize("auto_connect", [False, True])
@pytest.mark.parametrize("setting", ["off", "on-global", "on-provider"])
def test_email_authentication(
    db,
    setting,
    settings,
    user_factory,
    sociallogin_factory,
    client,
    rf,
    mailoutbox,
    auto_connect,
    with_emailaddress,
):
    """Tests that when an already existing email is given at the social signup
    form, enumeration preventation kicks in.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    if setting == "on-global":
        settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
    elif setting == "on-provider":
        settings.SOCIALACCOUNT_PROVIDERS = copy.deepcopy(
            settings.SOCIALACCOUNT_PROVIDERS
        )
        settings.SOCIALACCOUNT_PROVIDERS["openid_connect"][
            "EMAIL_AUTHENTICATION"
        ] = True
    else:
        settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION = False
    settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = auto_connect

    user = user_factory(with_emailaddress=with_emailaddress)

    sociallogin = sociallogin_factory(email=user.email, provider="unittest-server")

    request = rf.get("/")
    SessionMiddleware(lambda request: None).process_request(request)
    MessageMiddleware(lambda request: None).process_request(request)
    request.user = AnonymousUser()
    with context.request_context(request):
        with patch(
            "allauth.socialaccount.signals.social_account_updated.send"
        ) as updated_signal:
            with patch(
                "allauth.socialaccount.signals.social_account_added.send"
            ) as added_signal:
                resp = complete_social_login(request, sociallogin)
    if setting == "off":
        assert resp["location"] == reverse("account_email_verification_sent")
        assert not added_signal.called
        assert not updated_signal.called
    else:
        if with_emailaddress:
            assert resp["location"] == "/accounts/profile/"
        else:
            # user.email is set, but not verified.
            assert resp["location"] == reverse("account_email_verification_sent")
        assert get_user_model().objects.count() == 1
        assert SocialAccount.objects.filter(user=user.pk).exists() == auto_connect
        assert added_signal.called == auto_connect
        assert not updated_signal.called


def test_login_cancelled(client):
    resp = client.get(reverse("socialaccount_login_cancelled"))
    assert resp.status_code == 200
    assertTemplateUsed(resp, "socialaccount/login_cancelled.html")
