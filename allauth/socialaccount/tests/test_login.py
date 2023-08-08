import uuid

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount


def test_email_authentication(
    db, settings, user_factory, sociallogin_factory, client, rf, mailoutbox
):
    """Tests that when an already existing email is given at the social signup
    form, enumeration preventation kicks in.
    """
    settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True

    user = user_factory()
    account = SocialAccount.objects.create(
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
    assert resp["location"] == "/accounts/profile/"
