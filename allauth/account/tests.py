from datetime import timedelta

from django.utils.timezone import now
from django.test.utils import override_settings
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core import mail
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser

from allauth.account.forms import BaseSignupForm
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.utils import get_user_model

from . import app_settings

from .adapter import get_adapter

User = get_user_model()

@override_settings \
    (ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.MANDATORY,
     ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME,
     ACCOUNT_SIGNUP_FORM_CLASS=None,
     ACCOUNT_EMAIL_SUBJECT_PREFIX=None,
     ACCOUNT_ADAPTER='allauth.account.adapter.DefaultAccountAdapter',
     ACCOUNT_USERNAME_REQUIRED=True)
class AccountTests(TestCase):
    def setUp(self):
        if 'allauth.socialaccount' in settings.INSTALLED_APPS:
            # Otherwise ImproperlyConfigured exceptions may occur
            from ..socialaccount.models import SocialApp
            sa = SocialApp.objects.create(name='testfb',
                                          provider='facebook')
            sa.sites.add(Site.objects.get_current())


    def test_signup_same_email_verified_externally(self):
        user = self._test_signup_email_verified_externally('john@doe.com',
                                                           'john@doe.com')
        self.assertEquals(EmailAddress.objects.filter(user=user).count(),
                          1)
        EmailAddress.objects.get(verified=True,
                                 email='john@doe.com',
                                 user=user,
                                 primary=True)

    def test_signup_other_email_verified_externally(self):
        """
        John is invited on john@work.com, but signs up via john@home.com.
        E-mail verification is by-passed, his home e-mail address is
        used as a secondary.
        """
        user = self._test_signup_email_verified_externally('john@home.com',
                                                           'john@work.com')
        self.assertEquals(EmailAddress.objects.filter(user=user).count(),
                          2)
        EmailAddress.objects.get(verified=False,
                                 email='john@home.com',
                                 user=user,
                                 primary=False)
        EmailAddress.objects.get(verified=True,
                                 email='john@work.com',
                                 user=user,
                                 primary=True)

    def _test_signup_email_verified_externally(self, signup_email, verified_email):
        username = 'johndoe'
        request = RequestFactory().post(reverse('account_signup'),
                      { 'username': username,
                        'email': signup_email,
                        'password1': 'johndoe',
                        'password2': 'johndoe' })
        # Fake stash_verified_email
        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)
        request.user = AnonymousUser()
        request.session['account_verified_email'] = verified_email
        from .views import signup
        resp = signup(request)
        self.assertEquals(resp.status_code, 302)
        self.assertEquals(resp['location'], 
                          get_adapter().get_login_redirect_url(request))
        self.assertEquals(len(mail.outbox), 0)
        return User.objects.get(username=username)


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
            self.assertEquals(EmailConfirmation.objects.filter(email_address__email='john@doe.com').count(), 
                              attempt)
            # Wait for cooldown
            EmailConfirmation.objects.update(sent=now()
                                             - timedelta(days=1))
        # Verify, and re-attempt to login.
        confirmation = EmailConfirmation \
            .objects \
            .filter(email_address__user__username='johndoe')[:1] \
            .get()
        resp = c.post(reverse('account_confirm_email',
                       args=[confirmation.key]))
        self.assertEquals(resp['location'],
                          'http://testserver'+app_settings.EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL)





    def test_email_escaping(self):
        site = Site.objects.get_current()
        site.name = '<enc&"test>'
        site.save()
        u = User.objects.create(username='test',
                                email='foo@bar.com')
        request = RequestFactory().get('/')
        EmailAddress.objects.add_email(request, u, u.email, confirm=True)
        self.assertTrue(mail.outbox[0].subject[1:].startswith(site.name))


class BaseSignupFormTests(TestCase):

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_USERNAME_BLACKLIST=['username'])
    def test_username_in_blacklist(self):
        data = {
            'username': 'username',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data)
        self.assertFalse(form.is_valid())

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_USERNAME_BLACKLIST=['username'])
    def test_username_not_in_blacklist(self):
        data = {
            'username': 'theusername',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data)
        self.assertTrue(form.is_valid())
