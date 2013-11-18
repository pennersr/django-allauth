from __future__ import absolute_import

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


@override_settings(
    ACCOUNT_DEFAULT_HTTP_PROTOCOL='https',
    ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod.MANDATORY,
    ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME,
    ACCOUNT_SIGNUP_FORM_CLASS=None,
    ACCOUNT_EMAIL_SUBJECT_PREFIX=None,
    LOGIN_REDIRECT_URL='/accounts/profile/',
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

    @override_settings \
        (ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL)
    def test_username_containing_at(self):
        user = User.objects.create(username='@raymond.penners')
        user.set_password('psst')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='raymond.penners@gmail.com',
                                    primary=True,
                                    verified=True)
        resp = self.client.post(reverse('account_login'),
                                {'login': '@raymond.penners',
                                 'password': 'psst'})
        self.assertEqual(resp['location'],
                         'http://testserver'+settings.LOGIN_REDIRECT_URL)

    def test_signup_same_email_verified_externally(self):
        user = self._test_signup_email_verified_externally('john@doe.com',
                                                           'john@doe.com')
        self.assertEqual(EmailAddress.objects.filter(user=user).count(),
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
        self.assertEqual(EmailAddress.objects.filter(user=user).count(),
                         2)
        EmailAddress.objects.get(verified=False,
                                 email='john@home.com',
                                 user=user,
                                 primary=False)
        EmailAddress.objects.get(verified=True,
                                 email='john@work.com',
                                 user=user,
                                 primary=True)

    def _test_signup_email_verified_externally(self, signup_email,
                                               verified_email):
        username = 'johndoe'
        request = RequestFactory().post(reverse('account_signup'),
                                        {'username': username,
                                         'email': signup_email,
                                         'password1': 'johndoe',
                                         'password2': 'johndoe'})
        # Fake stash_verified_email
        from django.contrib.messages.middleware import MessageMiddleware
        from django.contrib.sessions.middleware import SessionMiddleware
        SessionMiddleware().process_request(request)
        MessageMiddleware().process_request(request)
        request.user = AnonymousUser()
        request.session['account_verified_email'] = verified_email
        from .views import signup
        resp = signup(request)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         get_adapter().get_login_redirect_url(request))
        self.assertEqual(len(mail.outbox), 0)
        return User.objects.get(username=username)

    def test_redirect_when_authenticated(self):
        user = User.objects.create(username='john',
                                   is_active=True)
        user.set_password('doe')
        user.save()
        c = Client()
        c.login(username='john', password='doe')
        resp = c.get(reverse('account_login'))
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://testserver/accounts/profile/',
                         resp['location'])

    def test_password_set_redirect(self):
        resp = self._password_set_or_reset_redirect('account_set_password',
                                                    True)
        self.assertEqual(resp.status_code, 302)

    def test_password_reset_no_redirect(self):
        resp = self._password_set_or_reset_redirect('account_change_password',
                                                    True)
        self.assertEqual(resp.status_code, 200)

    def test_password_set_no_redirect(self):
        resp = self._password_set_or_reset_redirect('account_set_password',
                                                    False)
        self.assertEqual(resp.status_code, 200)

    def test_password_reset_redirect(self):
        resp = self._password_set_or_reset_redirect('account_change_password',
                                                    False)
        self.assertEqual(resp.status_code, 302)

    def _password_set_or_reset_redirect(self, urlname, usable_password):
        c = Client()
        user = User.objects.create(username='john',
                                   is_active=True)
        user.set_password('doe')
        user.save()
        c = Client()
        c.login(username='john', password='doe')
        if not usable_password:
            user.set_unusable_password()
            user.save()
        resp = c.get(reverse(urlname))
        return resp

    def test_password_forgotten_url_protocol(self):
        c = Client()
        user = User.objects.create(username='john',
                                   email='john@doe.org',
                                   is_active=True)
        user.set_password('doe')
        user.save()
        resp = c.post(reverse('account_reset_password'),
                      data={'email': 'john@doe.org'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['john@doe.org'])
        self.assertGreater(mail.outbox[0].body.find('https://'), 0)
        return resp

    def test_email_verification_mandatory(self):
        c = Client()
        # Signup
        resp = c.post(reverse('account_signup'),
                      {'username': 'johndoe',
                       'email': 'john@doe.com',
                       'password1': 'johndoe',
                       'password2': 'johndoe'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mail.outbox[0].to, ['john@doe.com'])
        self.assertEqual(len(mail.outbox), 1)
        self.assertTemplateUsed(resp,
                                'account/verification_sent.html')
        self.assertTemplateUsed(resp,
                                'account/email/email_confirmation_signup_subject.txt')
        # Attempt to login, unverified
        for attempt in [1, 2]:
            resp = c.post(reverse('account_login'),
                          {'login': 'johndoe',
                           'password': 'johndoe'})
            # is_active is controlled by the admin to manually disable
            # users. I don't want this flag to flip automatically whenever
            # users verify their email adresses.
            self.assertTrue(User.objects.filter(username='johndoe',
                                                is_active=True).exists())
            self.assertTemplateUsed(resp,
                                    'account/verification_sent.html')
            self.assertEqual(len(mail.outbox), attempt)
            self.assertEqual(EmailConfirmation.objects
                             .filter(email_address__email=
                                     'john@doe.com').count(),
                             attempt)
            if attempt == 2:
                self.assertTemplateUsed(resp,
                                        'account/email/email_confirmation_subject.txt')

            # Wait for cooldown
            EmailConfirmation.objects.update(sent=now()
                                             - timedelta(days=1))
        # Verify, and re-attempt to login.
        confirmation = EmailConfirmation \
            .objects \
            .filter(email_address__user__username='johndoe')[:1] \
            .get()
        c.post(reverse('account_confirm_email',
                       args=[confirmation.key]))
        resp = c.post(reverse('account_login'),
                      {'login': 'johndoe',
                       'password': 'johndoe'})
        self.assertEqual(resp['location'],
                         'http://testserver'+settings.LOGIN_REDIRECT_URL)

    def test_email_escaping(self):
        site = Site.objects.get_current()
        site.name = '<enc&"test>'
        site.save()
        u = User.objects.create(username='test',
                                email='foo@bar.com')
        request = RequestFactory().get('/')
        EmailAddress.objects.add_email(request, u, u.email, confirm=True)
        self.assertTrue(mail.outbox[0].subject[1:].startswith(site.name))

    def test_login_view(self):
        c = Client()
        c.get(reverse('account_login'))
        # TODO: Actually test something

    def test_email_view(self):
        c = Client()
        c.get(reverse('account_email'))
        # TODO: Actually test something

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_logout_view_on_get(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    @override_settings(ACCOUNT_LOGOUT_ON_GET=False)
    def test_logout_view_on_post(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(resp, 'account/logout.html')
        resp = c.post(reverse('account_logout'))
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    def _logout_view(self, method):
        c = Client()
        user = User.objects.create(username='john',
                                   is_active=True)
        user.set_password('doe')
        user.save()
        c = Client()
        c.login(username='john', password='doe')
        return c, getattr(c, method)(reverse('account_logout'))

    @override_settings(ACCOUNT_EMAIL_VERIFICATION=app_settings
                       .EmailVerificationMethod.OPTIONAL)
    def test_optional_email_verification(self):
        c = Client()
        # Signup
        c.get(reverse('account_signup'))
        resp = c.post(reverse('account_signup'),
                      {'username': 'johndoe',
                       'email': 'john@doe.com',
                       'password1': 'johndoe',
                       'password2': 'johndoe'})
        # Logged in
        self.assertEqual(resp['location'],
                         'http://testserver'+settings.LOGIN_REDIRECT_URL)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(mail.outbox[0].to, ['john@doe.com'])
        self.assertEqual(len(mail.outbox), 1)
        # Logout & login again
        c.logout()
        # Wait for cooldown
        EmailConfirmation.objects.update(sent=now() - timedelta(days=1))
        # Signup
        resp = c.post(reverse('account_login'),
                      {'login': 'johndoe',
                       'password': 'johndoe'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['location'],
                         'http://testserver'+settings.LOGIN_REDIRECT_URL)
        self.assertEqual(mail.outbox[0].to, ['john@doe.com'])
        # There was an issue that we sent out email confirmation mails
        # on each login in case of optional verification. Make sure
        # this is not the case:
        self.assertEqual(len(mail.outbox), 1)


class BaseSignupFormTests(TestCase):

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_USERNAME_BLACKLIST=['username'])
    def test_username_in_blacklist(self):
        data = {
            'username': 'username',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertFalse(form.is_valid())

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_USERNAME_BLACKLIST=['username'])
    def test_username_not_in_blacklist(self):
        data = {
            'username': 'theusername',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertTrue(form.is_valid())
