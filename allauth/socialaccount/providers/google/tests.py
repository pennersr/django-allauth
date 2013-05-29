from django.conf import settings
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.test.client import RequestFactory
from django.test.utils import override_settings

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.account import app_settings as account_settings
from allauth.account.models import EmailConfirmation, EmailAddress
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers import registry
from allauth.tests import MockedResponse
from allauth.account.signals import user_signed_up
from allauth.account.adapter import get_adapter

from .provider import GoogleProvider

@override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                   ACCOUNT_SIGNUP_FORM_CLASS=None,
                   ACCOUNT_EMAIL_VERIFICATION \
                   =account_settings.EmailVerificationMethod.MANDATORY)
class GoogleTests(create_oauth2_tests(registry.by_id(GoogleProvider.id))):

    def get_mocked_response(self, verified_email=True):
        return MockedResponse(200, """
{"family_name": "Penners", "name": "Raymond Penners",
               "picture": "https://lh5.googleusercontent.com/-GOFYGBVOdBQ/AAAAAAAAAAI/AAAAAAAAAGM/WzRfPkv4xbo/photo.jpg",
               "locale": "nl", "gender": "male",
               "email": "raymond.penners@gmail.com",
               "link": "https://plus.google.com/108204268033311374519",
               "given_name": "Raymond", "id": "108204268033311374519",
                "verified_email": %s }
""" % (repr(verified_email).lower()))

    def test_email_verified(self):
        test_email = 'raymond.penners@gmail.com'
        self.login(self.get_mocked_response(verified_email=True))
        EmailAddress.objects \
            .get(email=test_email,
                 verified=True)
        self.assertFalse(EmailConfirmation.objects \
                             .filter(email_address__email=test_email) \
                             .exists())

    def test_user_signed_up_signal(self):
        sent_signals = []

        def on_signed_up(sender, request, user, **kwargs):
            sociallogin = kwargs['sociallogin']
            self.assertEqual(sociallogin.account.provider,
                              GoogleProvider.id)
            self.assertEqual(sociallogin.account.user,
                              user)
            sent_signals.append(sender)

        user_signed_up.connect(on_signed_up)
        self.login(self.get_mocked_response(verified_email=True))
        self.assertTrue(len(sent_signals) > 0)

    def test_email_unverified(self):
        test_email = 'raymond.penners@gmail.com'
        self.login(self.get_mocked_response(verified_email=False))
        email_address = EmailAddress.objects \
            .get(email=test_email)
        self.assertFalse(email_address.verified)
        self.assertTrue(EmailConfirmation.objects \
                            .filter(email_address__email=test_email) \
                            .exists())


    def test_email_verified_stashed(self):
        # http://slacy.com/blog/2012/01/how-to-set-session-variables-in-django-unit-tests/
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
        request = RequestFactory().get('/')
        request.session = self.client.session
        adapter = get_adapter()
        test_email = 'raymond.penners@gmail.com'
        adapter.stash_verified_email(request, test_email)
        request.session.save()

        self.login(self.get_mocked_response(verified_email=False))
        email_address = EmailAddress.objects \
            .get(email=test_email)
        self.assertTrue(email_address.verified)
        self.assertFalse(EmailConfirmation.objects \
                             .filter(email_address__email=test_email) \
                             .exists())




    def test_account_connect(self):
        email = 'some@mail.com'
        user = User.objects.create(username='user',
                                   is_active=True,
                                   email=email)
        user.set_password('test')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email=email,
                                    primary=True,
                                    verified=True)
        self.client.login(username=user.username,
                          password='test')
        self.login(self.get_mocked_response(verified_email=True))
        # Check if we connected...
        self.assertTrue(SocialAccount.objects.filter(user=user,
                                                     provider=GoogleProvider.id).exists())
        # For now, we do not pick up any new e-mail addresses on connect
        self.assertEqual(EmailAddress.objects.filter(user=user).count(), 1)
        self.assertEqual(EmailAddress.objects.filter(user=user,
                                                      email=email).count(), 1)
