import copy
from unittest.mock import ANY, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

import pytest
from pytest_django.asserts import assertTemplateUsed

from allauth.account.authentication import AUTHENTICATION_METHODS_SESSION_KEY
from allauth.core import context
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount, SocialToken
from allauth.socialaccount.providers.base import AuthProcess


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


@pytest.mark.parametrize("store_tokens", [False, True])
@pytest.mark.parametrize(
    "process,did_record",
    [
        (AuthProcess.LOGIN, True),
        (AuthProcess.CONNECT, False),
    ],
)
def test_record_authentication(
    db,
    sociallogin_factory,
    client,
    rf,
    user,
    process,
    did_record,
    store_tokens,
    settings,
):
    settings.SOCIALACCOUNT_STORE_TOKENS = store_tokens
    sociallogin = sociallogin_factory(provider="unittest-server", uid="123")
    sociallogin.state["process"] = process
    sociallogin.token = SocialToken(
        app=sociallogin.account.get_provider().app, token="123", token_secret="456"
    )
    SocialAccount.objects.create(user=user, uid="123", provider="unittest-server")
    request = rf.get("/")
    SessionMiddleware(lambda request: None).process_request(request)
    MessageMiddleware(lambda request: None).process_request(request)
    request.user = AnonymousUser()
    with context.request_context(request):
        complete_social_login(request, sociallogin)
    if did_record:
        assert request.session[AUTHENTICATION_METHODS_SESSION_KEY] == [
            {
                "at": ANY,
                "provider": sociallogin.account.provider,
                "method": "socialaccount",
                "uid": "123",
            }
        ]
    else:
        assert AUTHENTICATION_METHODS_SESSION_KEY not in request.session
    assert (
        SocialToken.objects.filter(
            account__uid="123", token="123", token_secret="456"
        ).exists()
        == store_tokens
    )
