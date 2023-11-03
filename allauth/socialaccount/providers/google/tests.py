import json
from datetime import datetime, timedelta
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse

from allauth.account import app_settings as account_settings
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.account.signals import user_signed_up
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.apple.client import jwt_encode
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import TestCase

from .provider import GoogleProvider


@override_settings(
    SOCIALACCOUNT_AUTO_SIGNUP=True,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.MANDATORY,
)
class GoogleTests(OAuth2TestsMixin, TestCase):
    provider_id = GoogleProvider.id

    def setUp(self):
        super().setUp()
        self.email = "raymond.penners@example.com"
        self.identity_overwrites = {}

    def get_google_id_token_payload(self):
        now = datetime.utcnow()
        client_id = "app123id"  # Matches `setup_app`
        payload = {
            "iss": "https://accounts.google.com",
            "azp": client_id,
            "aud": client_id,
            "sub": "108204268033311374519",
            "hd": "example.com",
            "email": self.email,
            "email_verified": True,
            "at_hash": "HK6E_P6Dh8Y93mRNtsDB1Q",
            "name": "Raymond Penners",
            "picture": "https://lh5.googleusercontent.com/photo.jpg",
            "given_name": "Raymond",
            "family_name": "Penners",
            "locale": "en",
            "iat": now,
            "exp": now + timedelta(hours=1),
        }
        payload.update(self.identity_overwrites)
        return payload

    def get_login_response_json(self, with_refresh_token=True):
        data = {
            "access_token": "testac",
            "expires_in": 3600,
            "scope": "https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid",
            "token_type": "Bearer",
            "id_token": jwt_encode(self.get_google_id_token_payload(), "secret"),
        }
        return json.dumps(data)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        resp = self.login(resp_mock=None)
        self.assertRedirects(resp, reverse("socialaccount_signup"))

    def test_wrong_id_token_claim_values(self):
        wrong_claim_values = {
            "iss": "not-google",
            "exp": datetime.utcnow() - timedelta(seconds=1),
            "aud": "foo",
        }
        for key, value in wrong_claim_values.items():
            with self.subTest(key):
                self.identity_overwrites = {key: value}
                resp = self.login(resp_mock=None)
                self.assertTemplateUsed(
                    resp,
                    "socialaccount/authentication_error.%s"
                    % getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html"),
                )

    def test_username_based_on_email(self):
        self.identity_overwrites = {"given_name": "明", "family_name": "小"}
        self.login(resp_mock=None)
        user = User.objects.get(email=self.email)
        self.assertEqual(user.username, "raymond.penners")

    def test_email_verified(self):
        self.identity_overwrites = {"email_verified": True}
        self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email, verified=True)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )
        account = email_address.user.socialaccount_set.all()[0]
        self.assertEqual(account.extra_data["given_name"], "Raymond")

    def test_user_signed_up_signal(self):
        sent_signals = []

        def on_signed_up(sender, request, user, **kwargs):
            sociallogin = kwargs["sociallogin"]
            self.assertEqual(sociallogin.account.provider, GoogleProvider.id)
            self.assertEqual(sociallogin.account.user, user)
            sent_signals.append(sender)

        user_signed_up.connect(on_signed_up)
        self.login(resp_mock=None)
        self.assertTrue(len(sent_signals) > 0)

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=False)
    def test_email_unverified(self):
        self.identity_overwrites = {"email_verified": False}
        resp = self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email)
        self.assertFalse(email_address.verified)
        self.assertTrue(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )
        self.assertTemplateUsed(
            resp, "account/email/email_confirmation_signup_subject.txt"
        )

    def test_email_verified_stashed(self):
        # http://slacy.com/blog/2012/01/how-to-set-session-variables-in-django-unit-tests/
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        request = RequestFactory().get("/")
        request.session = self.client.session
        adapter = get_adapter()
        adapter.stash_verified_email(request, self.email)
        request.session.save()

        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email)
        self.assertTrue(email_address.verified)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )

    def test_account_connect(self):
        email = "user@example.com"
        user = User.objects.create(username="user", is_active=True, email=email)
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        self.client.login(username=user.username, password="test")
        self.identity_overwrites = {"email": email, "email_verified": True}
        self.login(resp_mock=None, process="connect")
        # Check if we connected...
        self.assertTrue(
            SocialAccount.objects.filter(user=user, provider=GoogleProvider.id).exists()
        )
        # For now, we do not pick up any new email addresses on connect
        self.assertEqual(EmailAddress.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailAddress.objects.filter(user=user, email=email).count(), 1)

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.MANDATORY,
        SOCIALACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.NONE,
    )
    def test_social_email_verification_skipped(self):
        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        email_address = EmailAddress.objects.get(email=self.email)
        self.assertFalse(email_address.verified)
        self.assertFalse(
            EmailConfirmation.objects.filter(email_address__email=self.email).exists()
        )

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.OPTIONAL,
        SOCIALACCOUNT_EMAIL_VERIFICATION=account_settings.EmailVerificationMethod.OPTIONAL,
    )
    def test_social_email_verification_optional(self):
        self.identity_overwrites = {"email_verified": False}
        self.login(resp_mock=None)
        self.assertEqual(len(mail.outbox), 1)
        self.login(resp_mock=None)
        self.assertEqual(len(mail.outbox), 1)


@override_settings(
    SOCIALACCOUNT_PROVIDERS={
        "google": {
            "APP": {
                "client_id": "app123id",
                "key": "google",
                "secret": "dummy",
            }
        }
    }
)
class AppInSettingsTests(GoogleTests):
    """
    Run the same set of tests but without having a SocialApp entry.
    """

    pass
