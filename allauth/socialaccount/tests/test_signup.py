from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from allauth.account import app_settings as account_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.core import context
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount, SocialLogin
from allauth.socialaccount.views import signup


@pytest.fixture
def setup_sociallogin_flow(request_factory):
    def f(client, sociallogin):
        request = request_factory.get("/")
        request.user = AnonymousUser()

        with context.request_context(request):
            resp = complete_social_login(request, sociallogin)
            session = client.session
            for k, v in request.session.items():
                session[k] = v
            session.save()
            return resp

    return f


@pytest.fixture
def email_address_clash(request_factory):
    def _email_address_clash(username, email):
        User = get_user_model()
        # Some existig user
        exi_user = User()
        user_username(exi_user, "test")
        exi_user_email = "test@example.com"
        user_email(exi_user, exi_user_email)
        exi_user.save()
        EmailAddress.objects.create(
            user=exi_user, email=exi_user_email, verified=True, primary=True
        )

        # A social user being signed up...
        account = SocialAccount(provider="twitter", uid="123")
        user = User()
        user_username(user, username)
        user_email(user, email)
        sociallogin = SocialLogin(
            user=user, account=account, email_addresses=[EmailAddress(email=email)]
        )

        # Signing up, should pop up the social signup form
        request = request_factory.get("/accounts/twitter/login/callback/")
        request.user = AnonymousUser()
        with context.request_context(request):
            resp = complete_social_login(request, sociallogin)
        return request, resp

    return _email_address_clash


def test_email_address_created(
    settings, db, client, setup_sociallogin_flow, sociallogin_factory
):
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    settings.ACCOUNT_SIGNUP_FORM_CLASS = None
    settings.ACCOUNT_EMAIL_VERIFICATION = account_settings.EmailVerificationMethod.NONE

    sociallogin = sociallogin_factory(
        email="test@example.com", email_verified=False, username="test"
    )
    setup_sociallogin_flow(client, sociallogin)

    user = get_user_model().objects.get(
        **{account_settings.USER_MODEL_USERNAME_FIELD: "test"}
    )
    assert SocialAccount.objects.filter(user=user, uid=sociallogin.account.uid).exists()
    assert EmailAddress.objects.filter(user=user, email=user_email(user)).exists()


def test_email_address_clash_username_required(
    db, client, settings, email_address_clash
):
    """Test clash on both username and email"""
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = True
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    request, resp = email_address_clash("test", "test@example.com")
    assert resp["location"] == reverse("socialaccount_signup")

    # POST different username/email to social signup form
    request.method = "POST"
    request.POST = {"username": "other", "email": "other@example.com"}
    with context.request_context(request):
        resp = signup(request)
    assert resp["location"] == "/accounts/profile/"
    user = get_user_model().objects.get(
        **{account_settings.USER_MODEL_EMAIL_FIELD: "other@example.com"}
    )
    assert user_username(user) == "other"


def test_email_address_clash_username_not_required(db, settings, email_address_clash):
    """Test clash while username is not required"""
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    request, resp = email_address_clash("test", "test@example.com")
    assert resp["location"] == reverse("socialaccount_signup")

    # POST email to social signup form (username not present)
    request.method = "POST"
    request.POST = {"email": "other@example.com"}
    with context.request_context(request):
        resp = signup(request)
    assert resp["location"] == "/accounts/profile/"
    user = get_user_model().objects.get(
        **{account_settings.USER_MODEL_EMAIL_FIELD: "other@example.com"}
    )
    assert user_username(user) != "test"


def test_email_address_clash_username_auto_signup(db, settings, email_address_clash):
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    # Clash on username, but auto signup still works
    request, resp = email_address_clash("test", "other@example.com")
    assert resp["location"] == "/accounts/profile/"
    user = get_user_model().objects.get(
        **{account_settings.USER_MODEL_EMAIL_FIELD: "other@example.com"}
    )
    assert user_username(user) != "test"


def test_populate_username_in_blacklist(db, settings, request_factory):
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_USERNAME_BLACKLIST = ["username", "username1", "username2"]
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = True
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    request = request_factory.get("/accounts/twitter/login/callback/")
    request.user = AnonymousUser()

    User = get_user_model()
    user = User()
    setattr(user, account_settings.USER_MODEL_USERNAME_FIELD, "username")
    setattr(
        user,
        account_settings.USER_MODEL_EMAIL_FIELD,
        "username@example.com",
    )

    account = SocialAccount(provider="twitter", uid="123")
    sociallogin = SocialLogin(user=user, account=account)
    with context.request_context(request):
        complete_social_login(request, sociallogin)

    assert request.user.username not in account_settings.USERNAME_BLACKLIST


def test_verified_email_change_at_signup(
    db, client, settings, sociallogin_factory, setup_sociallogin_flow
):
    """
    Test scenario for when the user changes email at social signup. Current
    behavior is that both the unverified and verified email are added, and
    that the user is allowed to pass because he did provide a verified one.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = False

    sociallogin = sociallogin_factory(email="verified@example.com")
    setup_sociallogin_flow(client, sociallogin)
    resp = client.get(reverse("socialaccount_signup"))
    form = resp.context["form"]
    assert form["email"].value() == "verified@example.com"
    resp = client.post(
        reverse("socialaccount_signup"),
        data={"email": "unverified@example.org"},
    )
    assertRedirects(resp, "/accounts/profile/", fetch_redirect_response=False)
    user = get_user_model().objects.all()[0]
    assert user_email(user) == "verified@example.com"
    assert EmailAddress.objects.filter(
        user=user,
        email="verified@example.com",
        verified=True,
        primary=True,
    ).exists()
    assert EmailAddress.objects.filter(
        user=user,
        email="unverified@example.org",
        verified=False,
        primary=False,
    ).exists()


def test_unverified_email_change_at_signup(
    db, client, settings, sociallogin_factory, setup_sociallogin_flow
):
    """
    Test scenario for when the user changes email at social signup, while
    his provider did not provide a verified email. In that case, email
    verification will kick in. Here, both email addresses are added as
    well.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = False

    User = get_user_model()
    sociallogin = sociallogin_factory(
        email="unverified@example.com", email_verified=False
    )
    setup_sociallogin_flow(client, sociallogin)
    resp = client.get(reverse("socialaccount_signup"))
    form = resp.context["form"]
    assert form["email"].value() == "unverified@example.com"
    resp = client.post(
        reverse("socialaccount_signup"),
        data={"email": "unverified@example.org"},
    )

    assertRedirects(resp, reverse("account_email_verification_sent"))
    user = User.objects.all()[0]
    assert user_email(user) == "unverified@example.org"
    assert EmailAddress.objects.filter(
        user=user,
        email="unverified@example.com",
        verified=False,
        primary=False,
    ).exists()
    assert EmailAddress.objects.filter(
        user=user,
        email="unverified@example.org",
        verified=False,
        primary=True,
    ).exists()


def test_unique_email_validation_signup(
    db, client, sociallogin_factory, settings, setup_sociallogin_flow
):
    settings.ACCOUNT_PREVENT_ENUMERATION = False
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = False
    User = get_user_model()
    email = "me@example.com"
    user = User.objects.create(email=email)
    EmailAddress.objects.create(email=email, user=user, verified=True)
    sociallogin = sociallogin_factory(email="me@example.com")
    setup_sociallogin_flow(client, sociallogin)
    resp = client.get(reverse("socialaccount_signup"))
    form = resp.context["form"]
    assert form["email"].value() == email
    resp = client.post(reverse("socialaccount_signup"), data={"email": email})
    assertFormError(
        resp.context["form"],
        "email",
        "An account already exists with this email address."
        " Please sign in to that account first, then connect"
        " your Unittest Server account.",
    )


def test_social_account_taken_at_signup(
    db, client, sociallogin_factory, settings, setup_sociallogin_flow
):
    """
    Test scenario for when the user signs up with a social account
    and uses email address in that social account. But upon seeing the
    verification screen, they realize that email address is somehow
    unusable for them, and so backs up and enters a different email
    address (and is forced to choose a new username) while providing
    the same social account token which is owned by their first attempt.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = True
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = False

    User = get_user_model()
    sociallogin = sociallogin_factory(email="me1@example.com", email_verified=False)
    setup_sociallogin_flow(client, sociallogin)
    resp = client.get(reverse("socialaccount_signup"))
    form = resp.context["form"]
    assert form["email"].value() == "me1@example.com"
    resp = client.post(
        reverse("socialaccount_signup"),
        data={"username": "me1", "email": "me1@example.com"},
    )
    assert resp.status_code == 302
    assert User.objects.count() == 1
    assert SocialAccount.objects.count() == 1

    resp = client.get(reverse("socialaccount_signup"))
    assertRedirects(resp, reverse("account_login"))


def test_email_address_required_missing_from_sociallogin(
    db, settings, sociallogin_factory, client, setup_sociallogin_flow
):
    """Tests that when the email address is missing from the sociallogin email
    verification kicks in.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True

    sociallogin = sociallogin_factory(with_email=False)
    resp = setup_sociallogin_flow(client, sociallogin)
    assert resp["location"] == reverse("socialaccount_signup")

    resp = client.post(reverse("socialaccount_signup"), {"email": "other@example.org"})
    assert resp["location"] == reverse("account_email_verification_sent")


def test_email_address_conflict_at_social_signup_form(
    db,
    settings,
    user_factory,
    sociallogin_factory,
    client,
    setup_sociallogin_flow,
    mailoutbox,
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

    user = user_factory()
    sociallogin = sociallogin_factory(with_email=False)

    resp = setup_sociallogin_flow(client, sociallogin)
    # Auto signup does not kick in as the `sociallogin` does not have an email.
    assert resp["location"] == reverse("socialaccount_signup")

    # Here, we input the already existing email.
    resp = client.post(reverse("socialaccount_signup"), {"email": user.email})
    assert mailoutbox[0].subject == "[example.com] Account Already Exists"
    assert resp["location"] == reverse("account_email_verification_sent")


def test_email_address_conflict_during_auto_signup(
    db,
    settings,
    user_factory,
    sociallogin_factory,
    client,
    mailoutbox,
    setup_sociallogin_flow,
):
    """Tests that when an already existing email is received from the provider,
    enumeration preventation kicks in.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True

    user = user_factory()
    sociallogin = sociallogin_factory(email=user.email, with_email=True)
    resp = setup_sociallogin_flow(client, sociallogin)
    assert resp["location"] == reverse("account_email_verification_sent")
    assert mailoutbox[0].subject == "[example.com] Account Already Exists"


def test_email_address_conflict_removes_conflicting_email(
    db,
    settings,
    user_factory,
    sociallogin_factory,
    client,
    mailoutbox,
    setup_sociallogin_flow,
):
    """Tests that when an already existing email is given at the social signup
    form, enumeration preventation kicks in.
    """
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_UNIQUE_EMAIL = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_AUTHENTICATION_METHOD = "email"
    settings.ACCOUNT_EMAIL_VERIFICATION = "optional"
    settings.SOCIALACCOUNT_AUTO_SIGNUP = True
    settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION = False

    user = user_factory(email_verified=False)
    sociallogin = sociallogin_factory(email=user.email, email_verified=False)

    resp = setup_sociallogin_flow(client, sociallogin)

    # Auto signup does not kick in as the `sociallogin` has a conflicting email.
    assert resp["location"] == reverse("socialaccount_signup")

    # Here, we input the already existing email.
    resp = client.post(reverse("socialaccount_signup"), {"email": "other@email.org"})
    assert mailoutbox[0].subject == "[example.com] Please Confirm Your Email Address"
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert EmailAddress.objects.filter(email=user.email).count() == 1


def test_signup_closed(
    settings,
    db,
    client,
    setup_sociallogin_flow,
    sociallogin_factory,
):
    sociallogin = sociallogin_factory(
        email="test@example.com", email_verified=False, username="test"
    )
    with patch(
        "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.is_open_for_signup"
    ) as iofs:
        iofs.return_value = False
        resp = setup_sociallogin_flow(client, sociallogin)
    assert b"Sign Up Closed" in resp.content
    assert not get_user_model().objects.exists()
