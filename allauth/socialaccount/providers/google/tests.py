from django.test.utils import override_settings

from allauth.socialaccount.tests import create_oauth2_tests
from allauth.account import app_settings as account_settings
from allauth.account.models import EmailConfirmation, EmailAddress
from allauth.socialaccount.providers import registry
from allauth.tests import MockedResponse
from allauth.account.signals import user_signed_up

from provider import GoogleProvider

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

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_SIGNUP_FORM_CLASS=None,
                       ACCOUNT_EMAIL_VERIFICATION
                       =account_settings.EmailVerificationMethod.MANDATORY)
    def test_email_verified(self):
        test_email = 'raymond.penners@gmail.com'
        self.login(self.get_mocked_response(verified_email=True))
        EmailAddress.objects \
            .get(email=test_email,
                 verified=True)
        self.assertFalse(EmailConfirmation.objects \
                             .filter(email_address__email=test_email) \
                             .exists())

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_SIGNUP_FORM_CLASS=None,
                       ACCOUNT_EMAIL_VERIFICATION
                       =account_settings.EmailVerificationMethod.MANDATORY)
    def test_user_signed_up_signal(self):
        sent_signals = []

        def on_signed_up(sender, request, user, **kwargs):
            sociallogin = kwargs['sociallogin']
            self.assertEquals(sociallogin.account.provider,
                              GoogleProvider.id)
            self.assertEquals(sociallogin.account.user,
                              user)
            sent_signals.append(sender)

        user_signed_up.connect(on_signed_up)
        self.login(self.get_mocked_response(verified_email=True))
        self.assertTrue(len(sent_signals) > 0)

    @override_settings(SOCIALACCOUNT_AUTO_SIGNUP=True,
                       ACCOUNT_SIGNUP_FORM_CLASS=None,
                       ACCOUNT_EMAIL_VERIFICATION
                       =account_settings.EmailVerificationMethod.MANDATORY)
    def test_email_unverified(self):
        test_email = 'raymond.penners@gmail.com'
        self.login(self.get_mocked_response(verified_email=False))
        email_address = EmailAddress.objects \
            .get(email=test_email)
        self.assertFalse(email_address.verified)
        self.assertTrue(EmailConfirmation.objects \
                            .filter(email_address__email=test_email) \
                            .exists())

