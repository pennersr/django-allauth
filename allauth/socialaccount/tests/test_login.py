import uuid

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

import pytest

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount


@pytest.mark.parametrize("setting", ["off", "on-global", "on-provider"])
def test_email_authentication(
    db, setting, settings, user_factory, sociallogin_factory, client, rf, mailoutbox
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
        settings.SOCIALACCOUNT_PROVIDERS["google"] = {"EMAIL_AUTHENTICATION": True}
    else:
        settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION = False

    user = user_factory()
    SocialAccount.objects.create(
        user=user,
        provider="google",
        uid=uuid.uuid4().hex,
    )

    sociallogin = sociallogin_factory(email=user.email, provider="google")

    request = rf.get("/")
    SessionMiddleware(lambda request: None).process_request(request)
    MessageMiddleware(lambda request: None).process_request(request)
    request.user = AnonymousUser()

    resp = complete_social_login(request, sociallogin)
    if setting == "off":
        assert resp["location"] == reverse("account_email_verification_sent")
    else:
        assert resp["location"] == "/accounts/profile/"
