from __future__ import absolute_import
import json

from datetime import timedelta

import django
from django.utils.timezone import now
from django.test.utils import override_settings
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core import mail
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser, AbstractUser
from django.db import models

import unittest

from allauth.tests import TestCase, patch
from allauth.account.forms import BaseSignupForm
from allauth.account.models import (
    EmailAddress,
    EmailConfirmation,
    EmailConfirmationHMAC)

from allauth.utils import (
    get_current_site,
    get_user_model,
    get_username_max_length)

from . import app_settings

from .auth_backends import AuthenticationBackend
from .adapter import get_adapter
from .utils import url_str_to_user_pk, user_pk_to_url_str

import uuid


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
            sa.sites.add(get_current_site())

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod
        .USERNAME_EMAIL)
    def test_username_containing_at(self):
        user = get_user_model().objects.create(username='@raymond.penners')
        user.set_password('psst')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='raymond.penners@gmail.com',
                                    primary=True,
                                    verified=True)
        resp = self.client.post(reverse('account_login'),
                                {'login': '@raymond.penners',
                                 'password': 'psst'})
        self.assertRedirects(resp,
                             'http://testserver'+settings.LOGIN_REDIRECT_URL,
                             fetch_redirect_response=False)

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
        E-mail verification is by-passed, their home e-mail address is
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
        return get_user_model().objects.get(username=username)

    def _create_user(self):
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()
        return user

    def _create_user_and_login(self):
        user = self._create_user()
        self.client.login(username='john', password='doe')
        return user

    def test_redirect_when_authenticated(self):
        self._create_user_and_login()
        c = self.client
        resp = c.get(reverse('account_login'))
        self.assertRedirects(resp, 'http://testserver/accounts/profile/',
                             fetch_redirect_response=False)

    def test_password_reset_get(self):
        resp = self.client.get(reverse('account_reset_password'))
        self.assertTemplateUsed(resp, 'account/password_reset.html')

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
        user = self._create_user_and_login()
        c = self.client
        if not usable_password:
            user.set_unusable_password()
            user.save()
        resp = c.get(reverse(urlname))
        return resp

    def test_password_forgotten_username_hint(self):
        user = self._request_new_password()
        body = mail.outbox[0].body
        assert user.username in body

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL)
    def test_password_forgotten_no_username_hint(self):
        user = self._request_new_password()
        body = mail.outbox[0].body
        assert user.username not in body

    def _request_new_password(self):
        user = get_user_model().objects.create(
            username='john', email='john@doe.org', is_active=True)
        user.set_password('doe')
        user.save()
        self.client.post(
            reverse('account_reset_password'),
            data={'email': 'john@doe.org'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['john@doe.org'])
        return user

    def test_password_reset_flow(self):
        """
        Tests the password reset flow: requesting a new password,
        receiving the reset link via email and finally resetting the
        password to a new value.
        """
        # Request new password
        user = self._request_new_password()
        body = mail.outbox[0].body
        self.assertGreater(body.find('https://'), 0)

        # Extract URL for `password_reset_from_key` view and access it
        url = body[body.find('/password/reset/'):].split()[0]
        resp = self.client.get(url)
        self.assertTemplateUsed(
            resp,
            'account/password_reset_from_key.%s' %
            app_settings.TEMPLATE_EXTENSION)
        self.assertFalse('token_fail' in resp.context_data)

        # Reset the password
        resp = self.client.post(url,
                                {'password1': 'newpass123',
                                 'password2': 'newpass123'})
        self.assertRedirects(resp,
                             reverse('account_reset_password_from_key_done'))

        # Check the new password is in effect
        user = get_user_model().objects.get(pk=user.pk)
        self.assertTrue(user.check_password('newpass123'))

        # Trying to reset the password against the same URL (or any other
        # invalid/obsolete URL) returns a bad token response
        resp = self.client.post(url,
                                {'password1': 'newpass123',
                                 'password2': 'newpass123'})
        self.assertTemplateUsed(
            resp,
            'account/password_reset_from_key.%s' %
            app_settings.TEMPLATE_EXTENSION)
        self.assertTrue(resp.context_data['token_fail'])

        # Same should happen when accessing the page directly
        response = self.client.get(url)
        self.assertTemplateUsed(
            response,
            'account/password_reset_from_key.%s' %
            app_settings.TEMPLATE_EXTENSION)
        self.assertTrue(response.context_data['token_fail'])

        # When in XHR views, it should respond with a 400 bad request
        # code, and the response body should contain the JSON-encoded
        # error from the adapter
        response = self.client.post(url,
                                    {'password1': 'newpass123',
                                     'password2': 'newpass123'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode('utf8'))
        self.assertTrue('form_errors' in data)
        self.assertTrue('__all__' in data['form_errors'])

    @override_settings(ACCOUNT_LOGIN_ON_PASSWORD_RESET=True)
    def test_password_reset_ACCOUNT_LOGIN_ON_PASSWORD_RESET(self):
        user = self._request_new_password()
        body = mail.outbox[0].body
        url = body[body.find('/password/reset/'):].split()[0]
        resp = self.client.post(
            url,
            {'password1': 'newpass123',
             'password2': 'newpass123'})
        self.assertTrue(user.is_authenticated())
        # EmailVerificationMethod.MANDATORY sends us to the confirm-email page
        self.assertRedirects(resp, '/confirm-email/')

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=False)
    def test_email_verification_mandatory(self):
        c = Client()
        # Signup
        resp = c.post(reverse('account_signup'),
                      {'username': 'johndoe',
                       'email': 'john@doe.com',
                       'password1': 'johndoe',
                       'password2': 'johndoe'},
                      follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mail.outbox[0].to, ['john@doe.com'])
        self.assertGreater(mail.outbox[0].body.find('https://'), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTemplateUsed(
            resp,
            'account/verification_sent.%s' % app_settings.TEMPLATE_EXTENSION)
        # Attempt to login, unverified
        for attempt in [1, 2]:
            resp = c.post(reverse('account_login'),
                          {'login': 'johndoe',
                           'password': 'johndoe'},
                          follow=True)
            # is_active is controlled by the admin to manually disable
            # users. I don't want this flag to flip automatically whenever
            # users verify their email adresses.
            self.assertTrue(get_user_model().objects.filter(
                username='johndoe', is_active=True).exists())

            self.assertTemplateUsed(
                resp,
                'account/verification_sent.' + app_settings.TEMPLATE_EXTENSION)
            # Attempt 1: no mail is sent due to cool-down ,
            # but there was already a mail in the outbox.
            self.assertEqual(len(mail.outbox), attempt)
            self.assertEqual(
                EmailConfirmation.objects.filter(
                    email_address__email='john@doe.com').count(),
                attempt)
            # Wait for cooldown
            EmailConfirmation.objects.update(sent=now() - timedelta(days=1))
        # Verify, and re-attempt to login.
        confirmation = EmailConfirmation \
            .objects \
            .filter(email_address__user__username='johndoe')[:1] \
            .get()
        resp = c.get(reverse('account_confirm_email',
                             args=[confirmation.key]))
        self.assertTemplateUsed(
            resp,
            'account/email_confirm.%s' % app_settings.TEMPLATE_EXTENSION)
        c.post(reverse('account_confirm_email',
                       args=[confirmation.key]))
        resp = c.post(reverse('account_login'),
                      {'login': 'johndoe',
                       'password': 'johndoe'})
        self.assertRedirects(resp,
                             'http://testserver'+settings.LOGIN_REDIRECT_URL,
                             fetch_redirect_response=False)

    def test_email_escaping(self):
        site = get_current_site()
        site.name = '<enc&"test>'
        site.save()
        u = get_user_model().objects.create(
            username='test',
            email='foo@bar.com')
        request = RequestFactory().get('/')
        EmailAddress.objects.add_email(request, u, u.email, confirm=True)
        self.assertTrue(mail.outbox[0].subject[1:].startswith(site.name))

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod
        .OPTIONAL)
    def test_login_unverified_account_optional(self):
        """Tests login behavior when email verification is optional."""
        user = get_user_model().objects.create(username='john')
        user.set_password('doe')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='john@example.com',
                                    primary=True,
                                    verified=False)
        resp = self.client.post(reverse('account_login'),
                                {'login': 'john',
                                 'password': 'doe'})
        self.assertRedirects(resp,
                             'http://testserver'+settings.LOGIN_REDIRECT_URL,
                             fetch_redirect_response=False)

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod
        .OPTIONAL,
        ACCOUNT_LOGIN_ATTEMPTS_LIMIT=3)
    def test_login_failed_attempts_exceeded(self):
        user = get_user_model().objects.create(username='john')
        user.set_password('doe')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='john@example.com',
                                    primary=True,
                                    verified=False)
        for i in range(5):
            is_valid_attempt = (i == 4)
            is_locked = (i >= 3)
            resp = self.client.post(
                reverse('account_login'),
                {'login': 'john',
                 'password': (
                     'doe' if is_valid_attempt
                     else 'wrong')})
            self.assertFormError(
                resp,
                'form',
                None,
                'Too many failed login attempts. Try again later.'
                if is_locked
                else
                'The username and/or password you specified are not correct.')

    def test_login_unverified_account_mandatory(self):
        """Tests login behavior when email verification is mandatory."""
        user = get_user_model().objects.create(username='john')
        user.set_password('doe')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='john@example.com',
                                    primary=True,
                                    verified=False)
        resp = self.client.post(reverse('account_login'),
                                {'login': 'john',
                                 'password': 'doe'})
        self.assertRedirects(resp, reverse('account_email_verification_sent'))

    def test_login_inactive_account(self):
        """
        Tests login behavior with inactive accounts.

        Inactive user accounts should be prevented from performing any actions,
        regardless of their verified state.
        """
        # Inactive and verified user account
        user = get_user_model().objects.create(username='john',
                                               is_active=False)
        user.set_password('doe')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='john@example.com',
                                    primary=True,
                                    verified=True)
        resp = self.client.post(reverse('account_login'),
                                {'login': 'john',
                                 'password': 'doe'})
        self.assertRedirects(resp, reverse('account_inactive'))

        # Inactive and unverified user account
        user = get_user_model().objects.create(username='doe', is_active=False)
        user.set_password('john')
        user.save()
        EmailAddress.objects.create(user=user,
                                    email='doe@example.com',
                                    primary=True,
                                    verified=False)
        resp = self.client.post(reverse('account_login'),
                                {'login': 'doe',
                                 'password': 'john'})
        self.assertRedirects(resp, reverse('account_inactive'))

    def test_ajax_password_reset(self):
        get_user_model().objects.create(
            username='john', email='john@doe.org', is_active=True)
        resp = self.client.post(
            reverse('account_reset_password'),
            data={'email': 'john@doe.org'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['john@doe.org'])
        self.assertEqual(resp['content-type'], 'application/json')

    def test_ajax_login_fail(self):
        resp = self.client.post(reverse('account_login'),
                                {},
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 400)
        json.loads(resp.content.decode('utf8'))
        # TODO: Actually test something

    @override_settings(
        ACCOUNT_EMAIL_VERIFICATION=app_settings.EmailVerificationMethod
        .OPTIONAL)
    def test_ajax_login_success(self):
        user = get_user_model().objects.create(username='john', is_active=True)
        user.set_password('doe')
        user.save()
        resp = self.client.post(reverse('account_login'),
                                {'login': 'john',
                                 'password': 'doe'},
                                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['location'], '/accounts/profile/')

    def test_email_view(self):
        self._create_user_and_login()
        self.client.get(reverse('account_email'))
        # TODO: Actually test something

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_logout_view_on_get(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    @override_settings(ACCOUNT_LOGOUT_ON_GET=False)
    def test_logout_view_on_post(self):
        c, resp = self._logout_view('get')
        self.assertTemplateUsed(
            resp,
            'account/logout.%s' % app_settings.TEMPLATE_EXTENSION)
        resp = c.post(reverse('account_logout'))
        self.assertTemplateUsed(resp, 'account/messages/logged_out.txt')

    def _logout_view(self, method):
        c = Client()
        user = get_user_model().objects.create(username='john', is_active=True)
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
        self.assertRedirects(resp,
                             settings.LOGIN_REDIRECT_URL,
                             fetch_redirect_response=False)
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
        self.assertRedirects(resp,
                             settings.LOGIN_REDIRECT_URL,
                             fetch_redirect_response=False)
        self.assertEqual(mail.outbox[0].to, ['john@doe.com'])
        # There was an issue that we sent out email confirmation mails
        # on each login in case of optional verification. Make sure
        # this is not the case:
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS=False)
    def test_account_authenticated_login_redirects_is_false(self):
        self._create_user_and_login()
        resp = self.client.get(reverse('account_login'))
        self.assertEqual(resp.status_code, 200)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 9,
            }
        }])
    def test_django_password_validation(self):
        if django.VERSION < (1, 9, ):
            return
        resp = self.client.post(
            reverse('account_signup'),
            {'username': 'johndoe',
             'email': 'john@doe.com',
             'password1': 'johndoe',
             'password2': 'johndoe'})
        self.assertFormError(resp, 'form', None, [])
        self.assertFormError(
            resp,
            'form',
            'password1',
            ['This password is too short.'
             ' It must contain at least 9 characters.'])

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=True)
    def test_email_confirmation_hmac_falls_back(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user,
            email='a@b.com',
            verified=False,
            primary=True)
        confirmation = EmailConfirmation.create(email)
        confirmation.sent = now()
        confirmation.save()
        self.client.post(
            reverse('account_confirm_email',
                    args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertTrue(email.verified)

    @override_settings(ACCOUNT_EMAIL_CONFIRMATION_HMAC=True)
    def test_email_confirmation_hmac(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user,
            email='a@b.com',
            verified=False,
            primary=True)
        confirmation = EmailConfirmationHMAC(email)
        confirmation.send()
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(
            reverse('account_confirm_email',
                    args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertTrue(email.verified)

    @override_settings(
        ACCOUNT_EMAIL_CONFIRMATION_HMAC=True,
        ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS=0)
    def test_email_confirmation_hmac_timeout(self):
        user = self._create_user()
        email = EmailAddress.objects.create(
            user=user,
            email='a@b.com',
            verified=False,
            primary=True)
        confirmation = EmailConfirmationHMAC(email)
        confirmation.send()
        self.assertEqual(len(mail.outbox), 1)
        self.client.post(
            reverse('account_confirm_email',
                    args=[confirmation.key]))
        email = EmailAddress.objects.get(pk=email.pk)
        self.assertFalse(email.verified)


class EmailFormTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create(username='john',
                                        email='john1@doe.org')
        self.user.set_password('doe')
        self.user.save()
        self.email_address = EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True)
        self.email_address2 = EmailAddress.objects.create(
            user=self.user,
            email='john2@doe.org',
            verified=False,
            primary=False)
        self.client.login(username='john', password='doe')

    def test_add(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_add': '',
             'email': 'john3@doe.org'})
        EmailAddress.objects.get(
            email='john3@doe.org',
            user=self.user,
            verified=False,
            primary=False)
        self.assertTemplateUsed(resp,
                                'account/messages/email_confirmation_sent.txt')

    def test_ajax_add(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_add': '',
             'email': 'john3@doe.org'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['location'],
                         reverse('account_email'))

    def test_ajax_add_invalid(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_add': '',
             'email': 'john3#doe.org'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = json.loads(resp.content.decode('utf8'))
        self.assertTrue('form_errors' in data)
        self.assertTrue('email' in data['form_errors'])

    def test_remove_primary(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_remove': '',
             'email': self.email_address.email})
        EmailAddress.objects.get(pk=self.email_address.pk)
        self.assertTemplateUsed(
            resp,
            'account/messages/cannot_delete_primary_email.txt')

    def test_ajax_remove_primary(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_remove': '',
             'email': self.email_address.email},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTemplateUsed(
            resp,
            'account/messages/cannot_delete_primary_email.txt')
        data = json.loads(resp.content.decode('utf8'))
        self.assertEqual(data['location'],
                         reverse('account_email'))

    def test_remove_secondary(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_remove': '',
             'email': self.email_address2.email})
        self.assertRaises(EmailAddress.DoesNotExist,
                          lambda: EmailAddress.objects.get(
                              pk=self.email_address2.pk))
        self.assertTemplateUsed(
            resp,
            'account/messages/email_deleted.txt')

    def test_set_primary_unverified(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_primary': '',
             'email': self.email_address2.email})
        email_address = EmailAddress.objects.get(pk=self.email_address.pk)
        email_address2 = EmailAddress.objects.get(pk=self.email_address2.pk)
        self.assertFalse(email_address2.primary)
        self.assertTrue(email_address.primary)
        self.assertTemplateUsed(
            resp,
            'account/messages/unverified_primary_email.txt')

    def test_set_primary(self):
        email_address2 = EmailAddress.objects.get(pk=self.email_address2.pk)
        email_address2.verified = True
        email_address2.save()
        resp = self.client.post(
            reverse('account_email'),
            {'action_primary': '',
             'email': self.email_address2.email})
        email_address = EmailAddress.objects.get(pk=self.email_address.pk)
        email_address2 = EmailAddress.objects.get(pk=self.email_address2.pk)
        self.assertFalse(email_address.primary)
        self.assertTrue(email_address2.primary)
        self.assertTemplateUsed(
            resp,
            'account/messages/primary_email_set.txt')

    def test_verify(self):
        resp = self.client.post(
            reverse('account_email'),
            {'action_send': '',
             'email': self.email_address2.email})
        self.assertTemplateUsed(
            resp,
            'account/messages/email_confirmation_sent.txt')


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

    @override_settings(ACCOUNT_USERNAME_REQUIRED=True)
    def test_username_maxlength(self):
        data = {
            'username': 'username',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        max_length = get_username_max_length()
        field = form.fields['username']
        self.assertEqual(field.max_length, max_length)
        widget = field.widget
        self.assertEqual(widget.attrs.get('maxlength'), str(max_length))

    @override_settings(
        ACCOUNT_USERNAME_REQUIRED=True,
        ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE=True)
    def test_signup_email_verification(self):
        data = {
            'username': 'username',
            'email': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertFalse(form.is_valid())

        data = {
            'username': 'username',
            'email1': 'user@example.com',
            'email2': 'user@example.com',
        }
        form = BaseSignupForm(data, email_required=True)
        self.assertTrue(form.is_valid())

        data['email2'] = 'anotheruser@example.com'
        form = BaseSignupForm(data, email_required=True)
        self.assertFalse(form.is_valid())


class AuthenticationBackendTests(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(
            is_active=True,
            email='john@doe.com',
            username='john')
        user.set_password(user.username)
        user.save()
        self.user = user

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME)  # noqa
    def test_auth_by_username(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username),
            None)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.EMAIL)  # noqa
    def test_auth_by_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username),
            None)

    @override_settings(
        ACCOUNT_AUTHENTICATION_METHOD=app_settings.AuthenticationMethod.USERNAME_EMAIL)  # noqa
    def test_auth_by_username_or_email(self):
        user = self.user
        backend = AuthenticationBackend()
        self.assertEqual(
            backend.authenticate(
                username=user.email,
                password=user.username).pk,
            user.pk)
        self.assertEqual(
            backend.authenticate(
                username=user.username,
                password=user.username).pk,
            user.pk)


class UtilsTests(TestCase):
    def setUp(self):
        if hasattr(models, 'UUIDField'):
            self.user_id = uuid.uuid4().hex

            class UUIDUser(AbstractUser):
                id = models.UUIDField(primary_key=True,
                                      default=uuid.uuid4,
                                      editable=False)

                class Meta(AbstractUser.Meta):
                    swappable = 'AUTH_USER_MODEL'
        else:
            UUIDUser = get_user_model()
        self.UUIDUser = UUIDUser

    @unittest.skipUnless(hasattr(models, 'UUIDField'),
                         reason="No UUIDField in this django version")
    def test_url_str_to_pk_identifies_UUID_as_stringlike(self):
        with patch('allauth.account.utils.get_user_model') as mocked_gum:
            mocked_gum.return_value = self.UUIDUser
            self.assertEqual(url_str_to_user_pk(self.user_id),
                             self.user_id)

    def test_pk_to_url_string_identifies_UUID_as_stringlike(self):
        user = self.UUIDUser(
            is_active=True,
            email='john@doe.com',
            username='john')
        self.assertEquals(user_pk_to_url_str(user), str(user.pk))
