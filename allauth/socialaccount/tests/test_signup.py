import django
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

import allauth.app_settings
from allauth.account import app_settings as account_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import user_email, user_username
from allauth.core import context
from allauth.socialaccount import providers
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialLogin
from allauth.socialaccount.views import signup
from allauth.tests import TestCase


class SignupTests(TestCase):
    def setUp(self):
        super().setUp()
        for provider in providers.registry.get_class_list():
            if provider.id == "openid_connect":
                continue
            app = SocialApp.objects.create(
                provider=provider.id,
                name=provider.id,
                client_id="app123id",
                key="123",
                secret="dummy",
            )
            if allauth.app_settings.SITES_ENABLED:
                from django.contrib.sites.models import Site

                site = Site.objects.get_current()
                app.sites.add(site)

    @override_settings(
        SOCIALACCOUNT_AUTO_SIGNUP=True,
        ACCOUNT_SIGNUP_FORM_CLASS=None,
        ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.NONE,  # noqa
    )
    def test_email_address_created(self):
        factory = RequestFactory()
        request = factory.get("/accounts/login/callback/")
        request.user = AnonymousUser()
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)

        User = get_user_model()
        user = User()
        setattr(user, account_settings.USER_MODEL_USERNAME_FIELD, "test")
        setattr(user, account_settings.USER_MODEL_EMAIL_FIELD, "test@example.com")

        account = SocialAccount(provider="openid", uid="123")
        sociallogin = SocialLogin(user=user, account=account)
        with context.request_context(request):
            complete_social_login(request, sociallogin)

        user = User.objects.get(**{account_settings.USER_MODEL_USERNAME_FIELD: "test"})
        self.assertTrue(
            SocialAccount.objects.filter(user=user, uid=account.uid).exists()
        )
        self.assertTrue(
            EmailAddress.objects.filter(user=user, email=user_email(user)).exists()
        )

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=True,
    )
    def test_email_address_clash_username_required(self):
        """Test clash on both username and email"""
        request, resp = self._email_address_clash("test", "test@example.com")
        self.assertEqual(resp["location"], reverse("socialaccount_signup"))

        # POST different username/email to social signup form
        request.method = "POST"
        request.POST = {"username": "other", "email": "other@example.com"}
        with context.request_context(request):
            resp = signup(request)
        self.assertEqual(resp["location"], "/accounts/profile/")
        user = get_user_model().objects.get(
            **{account_settings.USER_MODEL_EMAIL_FIELD: "other@example.com"}
        )
        self.assertEqual(user_username(user), "other")

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=False,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=True,
    )
    def test_email_address_clash_username_not_required(self):
        """Test clash while username is not required"""
        request, resp = self._email_address_clash("test", "test@example.com")
        self.assertEqual(resp["location"], reverse("socialaccount_signup"))

        # POST email to social signup form (username not present)
        request.method = "POST"
        request.POST = {"email": "other@example.com"}
        with context.request_context(request):
            resp = signup(request)
        self.assertEqual(resp["location"], "/accounts/profile/")
        user = get_user_model().objects.get(
            **{account_settings.USER_MODEL_EMAIL_FIELD: "other@example.com"}
        )
        self.assertNotEqual(user_username(user), "test")

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=False,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=True,
    )
    def test_email_address_clash_username_auto_signup(self):
        # Clash on username, but auto signup still works
        request, resp = self._email_address_clash("test", "other@example.com")
        self.assertEqual(resp["location"], "/accounts/profile/")
        user = get_user_model().objects.get(
            **{account_settings.USER_MODEL_EMAIL_FIELD: "other@example.com"}
        )
        self.assertNotEqual(user_username(user), "test")

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_USERNAME_BLACKLIST=["username", "username1", "username2"],
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=True,
    )
    def test_populate_username_in_blacklist(self):
        factory = RequestFactory()
        request = factory.get("/accounts/twitter/login/callback/")
        request.user = AnonymousUser()
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)

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

        self.assertNotIn(request.user.username, account_settings.USERNAME_BLACKLIST)

    def _email_address_clash(self, username, email):
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
        sociallogin = SocialLogin(user=user, account=account)

        # Signing up, should pop up the social signup form
        factory = RequestFactory()
        request = factory.get("/accounts/twitter/login/callback/")
        request.user = AnonymousUser()
        SessionMiddleware(lambda request: None).process_request(request)
        MessageMiddleware(lambda request: None).process_request(request)
        with context.request_context(request):
            resp = complete_social_login(request, sociallogin)
        return request, resp

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=False,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=False,
    )
    def test_verified_email_change_at_signup(self):
        """
        Test scenario for when the user changes email at social signup. Current
        behavior is that both the unverified and verified email are added, and
        that the user is allowed to pass because he did provide a verified one.
        """
        session = self.client.session
        User = get_user_model()
        sociallogin = SocialLogin(
            user=User(email="verified@example.com"),
            account=SocialAccount(provider="google"),
            email_addresses=[
                EmailAddress(email="verified@example.com", verified=True, primary=True)
            ],
        )
        session["socialaccount_sociallogin"] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse("socialaccount_signup"))
        form = resp.context["form"]
        self.assertEqual(form["email"].value(), "verified@example.com")
        resp = self.client.post(
            reverse("socialaccount_signup"),
            data={"email": "unverified@example.org"},
        )
        self.assertRedirects(resp, "/accounts/profile/", fetch_redirect_response=False)
        user = User.objects.all()[0]
        self.assertEqual(user_email(user), "verified@example.com")
        self.assertTrue(
            EmailAddress.objects.filter(
                user=user,
                email="verified@example.com",
                verified=True,
                primary=True,
            ).exists()
        )
        self.assertTrue(
            EmailAddress.objects.filter(
                user=user,
                email="unverified@example.org",
                verified=False,
                primary=False,
            ).exists()
        )

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=False,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=False,
    )
    def test_unverified_email_change_at_signup(self):
        """
        Test scenario for when the user changes email at social signup, while
        his provider did not provide a verified email. In that case, email
        verification will kick in. Here, both email addresses are added as
        well.
        """
        session = self.client.session
        User = get_user_model()
        sociallogin = SocialLogin(
            user=User(email="unverified@example.com"),
            account=SocialAccount(provider="google"),
            email_addresses=[
                EmailAddress(
                    email="unverified@example.com",
                    verified=False,
                    primary=True,
                )
            ],
        )
        session["socialaccount_sociallogin"] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse("socialaccount_signup"))
        form = resp.context["form"]
        self.assertEqual(form["email"].value(), "unverified@example.com")
        resp = self.client.post(
            reverse("socialaccount_signup"),
            data={"email": "unverified@example.org"},
        )

        self.assertRedirects(resp, reverse("account_email_verification_sent"))
        user = User.objects.all()[0]
        self.assertEqual(user_email(user), "unverified@example.org")
        self.assertTrue(
            EmailAddress.objects.filter(
                user=user,
                email="unverified@example.com",
                verified=False,
                primary=False,
            ).exists()
        )
        self.assertTrue(
            EmailAddress.objects.filter(
                user=user,
                email="unverified@example.org",
                verified=False,
                primary=True,
            ).exists()
        )

    @override_settings(
        ACCOUNT_PREVENT_ENUMERATION=False,
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=False,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=False,
    )
    def test_unique_email_validation_signup(self):
        session = self.client.session
        User = get_user_model()
        email = "me@example.com"
        user = User.objects.create(email=email)
        EmailAddress.objects.create(email=email, user=user, verified=True)
        sociallogin = SocialLogin(
            user=User(email="me@example.com"),
            account=SocialAccount(provider="google"),
            email_addresses=[
                EmailAddress(email="me@example.com", verified=True, primary=True)
            ],
        )
        session["socialaccount_sociallogin"] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse("socialaccount_signup"))
        form = resp.context["form"]
        self.assertEqual(form["email"].value(), email)
        resp = self.client.post(reverse("socialaccount_signup"), data={"email": email})
        if django.VERSION >= (4, 1):
            self.assertFormError(
                resp.context["form"],
                "email",
                "An account already exists with this email address."
                " Please sign in to that account first, then connect"
                " your Google account.",
            )
        else:
            self.assertFormError(
                resp,
                "form",
                "email",
                "An account already exists with this email address."
                " Please sign in to that account first, then connect"
                " your Google account.",
            )

    @override_settings(
        ACCOUNT_EMAIL_REQUIRED=True,
        ACCOUNT_EMAIL_VERIFICATION="mandatory",
        ACCOUNT_UNIQUE_EMAIL=True,
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_AUTHENTICATION_METHOD="email",
        SOCIALACCOUNT_AUTO_SIGNUP=False,
    )
    def test_social_account_taken_at_signup(self):
        """
        Test scenario for when the user signs up with a social account
        and uses email address in that social account. But upon seeing the
        verification screen, they realize that email address is somehow
        unusable for them, and so backs up and enters a different email
        address (and is forced to choose a new username) while providing
        the same social account token which is owned by their first attempt.
        """
        session = self.client.session
        User = get_user_model()
        sociallogin = SocialLogin(
            user=User(email="me1@example.com"),
            account=SocialAccount(provider="facebook"),
        )
        session["socialaccount_sociallogin"] = sociallogin.serialize()
        session.save()
        resp = self.client.get(reverse("socialaccount_signup"))
        form = resp.context["form"]
        self.assertEqual(form["email"].value(), "me1@example.com")
        resp = self.client.post(
            reverse("socialaccount_signup"),
            data={"username": "me1", "email": "me1@example.com"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(SocialAccount.objects.count(), 1)

        resp = self.client.get(reverse("socialaccount_signup"))
        self.assertRedirects(resp, reverse("account_login"))


def test_email_address_required_missing_from_sociallogin(
    db, settings, sociallogin_factory, client, rf
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

    request = rf.get("/")
    request.session = {}
    request.user = AnonymousUser()
    resp = complete_social_login(request, sociallogin)
    assert resp["location"] == reverse("socialaccount_signup")

    session = client.session
    session["socialaccount_sociallogin"] = sociallogin.serialize()
    session.save()
    resp = client.post(reverse("socialaccount_signup"), {"email": "other@example.org"})
    assert resp["location"] == reverse("account_email_verification_sent")


def test_email_address_conflict_at_social_signup_form(
    db, settings, user_factory, sociallogin_factory, client, rf, mailoutbox
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

    request = rf.get("/")
    request.session = {}
    request.user = AnonymousUser()

    resp = complete_social_login(request, sociallogin)
    # Auto signup does not kick in as the `sociallogin` does not have an email.
    assert resp["location"] == reverse("socialaccount_signup")

    session = client.session
    session["socialaccount_sociallogin"] = sociallogin.serialize()
    session.save()
    # Here, we input the already existing email.
    resp = client.post(reverse("socialaccount_signup"), {"email": user.email})
    assert mailoutbox[0].subject == "[example.com] Account Already Exists"
    assert resp["location"] == reverse("account_email_verification_sent")


def test_email_address_conflict_during_auto_signup(
    db, settings, user_factory, sociallogin_factory, client, rf, mailoutbox
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

    request = rf.get("/")
    request.session = {}
    request.user = AnonymousUser()

    resp = complete_social_login(request, sociallogin)
    assert resp["location"] == reverse("account_email_verification_sent")
    assert mailoutbox[0].subject == "[example.com] Account Already Exists"


def test_email_address_conflict_removes_conflicting_email(
    db, settings, user_factory, sociallogin_factory, client, rf, mailoutbox
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

    request = rf.get("/")
    request.session = {}
    request.user = AnonymousUser()

    resp = complete_social_login(request, sociallogin)
    # Auto signup does not kick in as the `sociallogin` has a conflicting email.
    assert resp["location"] == reverse("socialaccount_signup")

    session = client.session
    session["socialaccount_sociallogin"] = sociallogin.serialize()
    session.save()
    # Here, we input the already existing email.
    resp = client.post(reverse("socialaccount_signup"), {"email": "other@email.org"})
    assert mailoutbox[0].subject == "[example.com] Please Confirm Your Email Address"
    assert resp["location"] == settings.LOGIN_REDIRECT_URL
    assert EmailAddress.objects.filter(email=user.email).count() == 1
