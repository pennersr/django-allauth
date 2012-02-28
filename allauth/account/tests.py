from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.core import mail

from emailconfirmation.models import EmailAddress

import utils
import app_settings

class AccountTests(TestCase):
    def setUp(self):
        app_settings.EMAIL_VERIFICATION = True
        app_settings.EMAIL_AUTHENTICATION = False

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
        self.assertTemplateUsed(resp,
                                'account/verification_sent.html')
        # Attempt to login, unverified
        resp = c.post(reverse('account_login'),
                      { 'username': 'johndoe',
                        'password': 'johndoe'})
        # is_active is controlled by the admin to manually disable
        # users. I don't want this flag to flip automatically whenever
        # users verify their email adresses.
        self.assertTrue(User.objects.filter(username='johndoe',
                                            is_active=True).exists())
        self.assertTemplateUsed(resp,
                                'account/verification_sent.html')
        # Verify, and re-attempt to login.
        EmailAddress.objects.filter(user__username='johndoe') \
            .update(verified=True)
        resp = c.post(reverse('account_login'),
                      { 'username': 'johndoe',
                        'password': 'johndoe'})
        self.assertEquals(resp['location'], 
                          'http://testserver'+settings.LOGIN_REDIRECT_URL)
        


            
        
