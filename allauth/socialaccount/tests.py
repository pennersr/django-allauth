import base64
import hashlib
import json
import random
import requests
import warnings
from urllib.parse import parse_qs, urlparse

import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.http import urlencode

import allauth.app_settings

from ..account import app_settings as account_settings
from ..account.models import EmailAddress
from ..account.utils import user_email, user_username
from ..tests import Mock, MockedResponse, TestCase, mocked_response, patch
from ..utils import get_user_model
from . import app_settings, providers
from .helpers import complete_social_login
from .models import SocialAccount, SocialApp, SocialLogin
from .views import signup


def setup_app(provider):
    app = None
    if not app_settings.PROVIDERS.get(provider.id, {}).get("APP"):
        app = SocialApp.objects.create(
            provider=provider.id,
            name=provider.id,
            client_id="app123id",
            key=provider.id,
            secret="dummy",
        )
        if allauth.app_settings.SITES_ENABLED:
            from django.contrib.sites.models import Site

            app.sites.add(Site.objects.get_current())
    return app


class OAuthTestsMixin(object):
    provider_id = None

    def get_mocked_response(self):
        pass

    def setUp(self):
        super(OAuthTestsMixin, self).setUp()
        self.provider = providers.registry.by_id(self.provider_id)
        self.app = setup_app(self.provider)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        resp_mocks = self.get_mocked_response()
        if resp_mocks is None:
            warnings.warn("Cannot test provider %s, no oauth mock" % self.provider.id)
            return
        resp = self.login(resp_mocks)
        self.assertRedirects(resp, reverse("socialaccount_signup"))
        resp = self.client.get(reverse("socialaccount_signup"))
        sociallogin = resp.context["form"].sociallogin
        data = dict(
            email=user_email(sociallogin.user),
            username=str(random.randrange(1000, 10000000)),
        )
        resp = self.client.post(reverse("socialaccount_signup"), data=data)
        self.assertRedirects(resp, "/accounts/profile/", fetch_redirect_response=False)
        user = resp.context["user"]
        self.assertFalse(user.has_usable_password())
        account = SocialAccount.objects.get(user=user, provider=self.provider.id)
        # The following lines don't actually test that much, but at least
        # we make sure that the code is hit.
        provider_account = account.get_provider_account()
        provider_account.get_avatar_url()
        provider_account.get_profile_url()
        provider_account.get_brand()
        provider_account.to_str()
        return account

    @override_settings(
        SOCIALACCOUNT_AUTO_SIGNUP=True,
        SOCIALACCOUNT_EMAIL_REQUIRED=False,
        ACCOUNT_EMAIL_REQUIRED=False,
    )
    def test_auto_signup(self):
        resp_mocks = self.get_mocked_response()
        if not resp_mocks:
            warnings.warn("Cannot test provider %s, no oauth mock" % self.provider.id)
            return
        resp = self.login(resp_mocks)
        self.assertRedirects(resp, "/accounts/profile/", fetch_redirect_response=False)
        self.assertFalse(resp.context["user"].has_usable_password())

    def login(self, resp_mocks, process="login"):
        with mocked_response(
            MockedResponse(
                200,
                "oauth_token=token&oauth_token_secret=psst",
                {"content-type": "text/html"},
            )
        ):
            resp = self.client.post(
                reverse(self.provider.id + "_login")
                + "?"
                + urlencode(dict(process=process))
            )
        p = urlparse(resp["location"])
        q = parse_qs(p.query)
        complete_url = reverse(self.provider.id + "_callback")
        self.assertGreater(q["oauth_callback"][0].find(complete_url), 0)
        with mocked_response(self.get_access_token_response(), *resp_mocks):
            resp = self.client.get(complete_url)
        return resp

    def get_access_token_response(self):
        return MockedResponse(
            200,
            "oauth_token=token&oauth_token_secret=psst",
            {"content-type": "text/html"},
        )

    def test_authentication_error(self):
        resp = self.client.get(reverse(self.provider.id + "_callback"))
        self.assertTemplateUsed(
            resp,
            "socialaccount/authentication_error.%s"
            % getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html"),
        )


# For backward-compatibility with third-party provider tests that call
# create_oauth_tests() rather than using the mixin directly.
def create_oauth_tests(provider):
    class Class(OAuthTestsMixin, TestCase):
        provider_id = provider.id

    Class.__name__ = "OAuthTests_" + provider.id
    return Class


class OAuth2TestsMixin(object):
    provider_id = None

    def get_mocked_response(self):
        pass

    def get_login_response_json(self, with_refresh_token=True):
        rt = ""
        if with_refresh_token:
            rt = ',"refresh_token": "testrf"'
        return (
            """{
            "uid":"weibo",
            "access_token":"testac"
            %s }"""
            % rt
        )

    def setUp(self):
        super(OAuth2TestsMixin, self).setUp()
        self.provider = providers.registry.by_id(self.provider_id)
        self.app = setup_app(self.provider)

    def test_provider_has_no_pkce_params(self):
        provider_settings = app_settings.PROVIDERS.get(self.provider_id, {})
        provider_settings_with_pkce_set = provider_settings.copy()
        provider_settings_with_pkce_set["OAUTH_PKCE_ENABLED"] = False

        with self.settings(
            SOCIALACCOUNT_PROVIDERS={self.provider_id: provider_settings_with_pkce_set}
        ):
            self.assertEqual(self.provider.get_pkce_params(), {})

    def test_provider_has_pkce_params(self):
        provider_settings = app_settings.PROVIDERS.get(self.provider_id, {})
        provider_settings_with_pkce_set = provider_settings.copy()
        provider_settings_with_pkce_set["OAUTH_PKCE_ENABLED"] = True

        with self.settings(
            SOCIALACCOUNT_PROVIDERS={self.provider_id: provider_settings_with_pkce_set}
        ):
            pkce_params = self.provider.get_pkce_params()
            self.assertEqual(
                set(pkce_params.keys()),
                {"code_challenge", "code_challenge_method", "code_verifier"},
            )
            hashed_verifier = hashlib.sha256(
                pkce_params["code_verifier"].encode("ascii")
            )
            code_challenge = base64.urlsafe_b64encode(hashed_verifier.digest())
            code_challenge_without_padding = code_challenge.rstrip(b"=")
            assert pkce_params["code_challenge"] == code_challenge_without_padding

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login(self):
        resp_mock = self.get_mocked_response()
        if not resp_mock:
            warnings.warn("Cannot test provider %s, no oauth mock" % self.provider.id)
            return
        resp = self.login(
            resp_mock,
        )
        self.assertRedirects(resp, reverse("socialaccount_signup"))

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login_with_pkce_disabled(self):
        provider_settings = app_settings.PROVIDERS.get(self.provider_id, {})
        provider_settings_with_pkce_disabled = provider_settings.copy()
        provider_settings_with_pkce_disabled["OAUTH_PKCE_ENABLED"] = False

        with self.settings(
            SOCIALACCOUNT_PROVIDERS={
                self.provider_id: provider_settings_with_pkce_disabled
            }
        ):
            resp_mock = self.get_mocked_response()
            if not resp_mock:
                warnings.warn(
                    "Cannot test provider %s, no oauth mock" % self.provider.id
                )
                return
            resp = self.login(
                resp_mock,
            )
            self.assertRedirects(resp, reverse("socialaccount_signup"))

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=False)
    def test_login_with_pkce_enabled(self):
        provider_settings = app_settings.PROVIDERS.get(self.provider_id, {})
        provider_settings_with_pkce_enabled = provider_settings.copy()
        provider_settings_with_pkce_enabled["OAUTH_PKCE_ENABLED"] = True
        with self.settings(
            SOCIALACCOUNT_PROVIDERS={
                self.provider_id: provider_settings_with_pkce_enabled
            }
        ):
            resp_mock = self.get_mocked_response()
            if not resp_mock:
                warnings.warn(
                    "Cannot test provider %s, no oauth mock" % self.provider.id
                )
                return

            resp = self.login(
                resp_mock,
            )
            self.assertRedirects(resp, reverse("socialaccount_signup"))

    def test_account_tokens(self, multiple_login=False):
        if not app_settings.STORE_TOKENS:
            return
        email = "user@example.com"
        user = get_user_model()(is_active=True)
        user_email(user, email)
        user_username(user, "user")
        user.set_password("test")
        user.save()
        EmailAddress.objects.create(user=user, email=email, primary=True, verified=True)
        self.client.login(username=user.username, password="test")
        self.login(self.get_mocked_response(), process="connect")
        if multiple_login:
            self.login(
                self.get_mocked_response(),
                with_refresh_token=False,
                process="connect",
            )
        # get account
        sa = SocialAccount.objects.filter(user=user, provider=self.provider.id).get()
        # The following lines don't actually test that much, but at least
        # we make sure that the code is hit.
        provider_account = sa.get_provider_account()
        provider_account.get_avatar_url()
        provider_account.get_profile_url()
        provider_account.get_brand()
        provider_account.to_str()
        # get token
        if self.app:
            t = sa.socialtoken_set.get()
            # verify access_token and refresh_token
            self.assertEqual("testac", t.token)
            self.assertEqual(
                t.token_secret,
                json.loads(self.get_login_response_json(with_refresh_token=True)).get(
                    "refresh_token", ""
                ),
            )

    def test_account_refresh_token_saved_next_login(self):
        """
        fails if a login missing a refresh token, deletes the previously
        saved refresh token. Systems such as google's oauth only send
        a refresh token on first login.
        """
        self.test_account_tokens(multiple_login=True)

    def login(self, resp_mock=None, process="login", with_refresh_token=True):
        resp = self.client.post(
            reverse(self.provider.id + "_login")
            + "?"
            + urlencode(dict(process=process))
        )

        p = urlparse(resp["location"])
        q = parse_qs(p.query)

        pkce_enabled = app_settings.PROVIDERS.get(self.provider_id, {}).get(
            "OAUTH_PKCE_ENABLED", self.provider.pkce_enabled_default
        )

        self.assertEqual("code_challenge" in q, pkce_enabled)
        self.assertEqual("code_challenge_method" in q, pkce_enabled)
        if pkce_enabled:
            code_challenge = q["code_challenge"][0]
            self.assertEqual(q["code_challenge_method"][0], "S256")

        complete_url = reverse(self.provider.id + "_callback")
        self.assertGreater(q["redirect_uri"][0].find(complete_url), 0)
        response_json = self.get_login_response_json(
            with_refresh_token=with_refresh_token
        )

        if isinstance(resp_mock, list):
            resp_mocks = resp_mock
        elif resp_mock is None:
            resp_mocks = []
        else:
            resp_mocks = [resp_mock]

        with mocked_response(
            MockedResponse(200, response_json, {"content-type": "application/json"}),
            *resp_mocks,
        ):
            resp = self.client.get(complete_url, self.get_complete_parameters(q))

            # Find the access token POST request, and assert that it contains
            # the correct code_verifier if and only if PKCE is enabled
            request_calls = requests.request.call_args_list
            for args, kwargs in request_calls:
                data = kwargs.get("data", {})
                if (
                    args[0] == "POST"
                    and isinstance(data, dict)
                    and data.get("redirect_uri", "").endswith(complete_url)
                ):
                    self.assertEqual("code_verifier" in data, pkce_enabled)

                    if pkce_enabled:
                        hashed_code_verifier = hashlib.sha256(
                            data["code_verifier"].encode("ascii")
                        )
                        expected_code_challenge = (
                            base64.urlsafe_b64encode(hashed_code_verifier.digest())
                            .rstrip(b"=")
                            .decode()
                        )
                        self.assertEqual(code_challenge, expected_code_challenge)

        return resp

    def get_complete_parameters(self, q):
        return {"code": "test", "state": q["state"][0]}

    def test_authentication_error(self):
        resp = self.client.get(reverse(self.provider.id + "_callback"))
        self.assertTemplateUsed(
            resp,
            "socialaccount/authentication_error.%s"
            % getattr(settings, "ACCOUNT_TEMPLATE_EXTENSION", "html"),
        )


# For backward-compatibility with third-party provider tests that call
# create_oauth2_tests() rather than using the mixin directly.
def create_oauth2_tests(provider):
    class Class(OAuth2TestsMixin, TestCase):
        provider_id = provider.id

    Class.__name__ = "OAuth2Tests_" + provider.id
    return Class


class OpenIDConnectTests(OAuth2TestsMixin):
    oidc_info_content = {
        "authorization_endpoint": "/login",
        "userinfo_endpoint": "/userinfo",
        "token_endpoint": "/token",
    }
    userinfo_content = {
        "picture": "https://secure.gravatar.com/avatar/123",
        "email": "ness@some.oidc.server.onett.example",
        "sub": 2187,
        "identities": [],
        "name": "Ness",
    }
    extra_data = {
        "picture": "https://secure.gravatar.com/avatar/123",
        "email": "ness@some.oidc.server.onett.example",
        "sub": 2187,
        "identities": [],
        "name": "Ness",
    }

    def setUp(self):
        super(OpenIDConnectTests, self).setUp()
        patcher = patch(
            "allauth.socialaccount.providers.openid_connect.views.requests",
            get=Mock(side_effect=self._mocked_responses),
        )
        self.mock_requests = patcher.start()
        self.addCleanup(patcher.stop)

    def get_mocked_response(self):
        # Enable test_login in OAuth2TestsMixin, but this response mock is unused
        return True

    def _mocked_responses(self, url, *args, **kwargs):
        if url.endswith("/.well-known/openid-configuration"):
            return MockedResponse(200, json.dumps(self.oidc_info_content))
        elif url.endswith("/userinfo"):
            return MockedResponse(200, json.dumps(self.userinfo_content))

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True)
    def test_login_auto_signup(self):
        resp = self.login()
        self.assertRedirects(resp, "/accounts/profile/", fetch_redirect_response=False)
        sa = SocialAccount.objects.get(provider=self.provider.id)
        self.assertDictEqual(sa.extra_data, self.extra_data)


class SocialAccountTests(TestCase):
    def setUp(self):
        super(SocialAccountTests, self).setUp()
        for provider in providers.registry.get_list():
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
        complete_social_login(request, sociallogin)

        self.assertNotIn(request.user.username, account_settings.USERNAME_BLACKLIST)

    def _email_address_clash(self, username, email):
        User = get_user_model()
        # Some existig user
        exi_user = User()
        user_username(exi_user, "test")
        user_email(exi_user, "test@example.com")
        exi_user.save()

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
        resp = complete_social_login(request, sociallogin)
        return request, resp

    def test_disconnect(self):
        User = get_user_model()
        # Some existig user
        user = User()
        user_username(user, "test")
        user_email(user, "test@example.com")
        user.set_password("test")
        user.save()

        account = SocialAccount.objects.create(uid="123", provider="twitter", user=user)

        self.client.login(username=user.username, password=user.username)
        resp = self.client.get(reverse("socialaccount_connections"))
        self.assertTemplateUsed(resp, "socialaccount/connections.html")
        resp = self.client.post(
            reverse("socialaccount_connections"), {"account": account.pk}
        )
        self.assertFalse(SocialAccount.objects.filter(pk=account.pk).exists())

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
        User.objects.create(email="me@example.com")
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
        self.assertEqual(form["email"].value(), "me@example.com")
        resp = self.client.post(
            reverse("socialaccount_signup"), data={"email": "me@example.com"}
        )
        if django.VERSION >= (4, 1):
            self.assertFormError(
                resp.context["form"],
                "email",
                "An account already exists with this e-mail address."
                " Please sign in to that account first, then connect"
                " your Google account.",
            )
        else:
            self.assertFormError(
                resp,
                "form",
                "email",
                "An account already exists with this e-mail address."
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

    def test_social_account_str_default(self):
        User = get_user_model()
        user = User(username="test")
        sa = SocialAccount(user=user)
        self.assertEqual("test", str(sa))

    def socialaccount_str_custom_formatter(socialaccount):
        return "A custom str builder for {}".format(socialaccount.user)

    @override_settings(
        SOCIALACCOUNT_SOCIALACCOUNT_STR=socialaccount_str_custom_formatter
    )
    def test_social_account_str_customized(self):
        User = get_user_model()
        user = User(username="test")
        sa = SocialAccount(user=user)
        self.assertEqual("A custom str builder for test", str(sa))
