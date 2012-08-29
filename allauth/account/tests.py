from datetime import timedelta
try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    now = datetime.now

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core import mail
from django.contrib.sites.models import Site

from allauth.account.models import EmailAddress, EmailConfirmation

from app_settings import AuthenticationMethod
import app_settings

class AccountTests(TestCase):
    def setUp(self):
        self.OLD_EMAIL_VERIFICATION = app_settings.EMAIL_VERIFICATION
        self.OLD_AUTHENTICATION_METHOD = app_settings.AUTHENTICATION_METHOD
        self.OLD_SIGNUP_FORM_CLASS = app_settings.SIGNUP_FORM_CLASS
        self.OLD_USERNAME_REQUIRED = app_settings.USERNAME_REQUIRED
        app_settings.EMAIL_VERIFICATION = True
        app_settings.AUTHENTICATION_METHOD = AuthenticationMethod.USERNAME
        app_settings.SIGNUP_FORM_CLASS = None
        app_settings.USERNAME_REQUIRED = True

        if 'allauth.socialaccount' in settings.INSTALLED_APPS:
            # Otherwise ImproperlyConfigured exceptions may occur
            from ..socialaccount.models import SocialApp
            SocialApp.objects.create(name='testfb',
                                     provider='facebook',
                                     site=Site.objects.get_current())

    def test_email_verification_mandatory(self):
        c = Client()
        # Signup
        resp = c.post(reverse('account_signup'),
                      { 'username': 'johndoe',
                        'email': 'john@doe.com',
                        'password1': 'johndoe',
                        'password2': 'johndoe' })
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(mail.outbox[0].to, ['john@doe.com'])
        self.assertEquals(len(mail.outbox), 1)
        self.assertTemplateUsed(resp,
                                'account/verification_sent.html')
        # Attempt to login, unverified
        for attempt in [1, 2]:
            resp = c.post(reverse('account_login'),
                          { 'login': 'johndoe',
                            'password': 'johndoe'})
            # is_active is controlled by the admin to manually disable
            # users. I don't want this flag to flip automatically whenever
            # users verify their email adresses.
            self.assertTrue(User.objects.filter(username='johndoe',
                                                is_active=True).exists())
            self.assertTemplateUsed(resp,
                                    'account/verification_sent.html')
            self.assertEquals(len(mail.outbox), attempt)
            # Wait for cooldown
            EmailConfirmation.objects.update(sent=now()
                                             - timedelta(days=1))
        # Verify, and re-attempt to login.
        EmailAddress.objects.filter(user__username='johndoe') \
            .update(verified=True)
        resp = c.post(reverse('account_login'),
                      { 'login': 'johndoe',
                        'password': 'johndoe'})
        self.assertEquals(resp['location'],
                          'http://testserver'+settings.LOGIN_REDIRECT_URL)





    def x_test_email_escaping(self):
        """
        Test is only valid if emailconfirmation is listed after
        allauth in INSTALLED_APPS
        """
        site = Site.objects.get_current()
        site.name = '<enc&"test>'
        site.save()
        u = User.objects.create(username='test',
                                email='foo@bar.com')
        EmailAddress.objects.add_email(u, u.email)

    def tearDown(self):
        app_settings.EMAIL_VERIFICATION = self.OLD_EMAIL_VERIFICATION
        app_settings.AUTHENTICATION_METHOD = self.OLD_AUTHENTICATION_METHOD
        app_settings.SIGNUP_FORM_CLASS = self.OLD_SIGNUP_FORM_CLASS
        app_settings.USERNAME_REQUIRED = self.OLD_USERNAME_REQUIRED

