from __future__ import absolute_import

import json

from django.core.exceptions import PermissionDenied
from django.db import models
from django.contrib.auth import authenticate
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible
from django.utils.crypto import get_random_string
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

import allauth.app_settings
from allauth.account.models import EmailAddress
from allauth.account.utils import get_next_redirect_url, setup_user_email
from allauth.utils import (get_user_model, serialize_instance,
                           deserialize_instance)

from . import providers
from .fields import JSONField


class SocialAppManager(models.Manager):
    def get_current(self, provider):
        site = Site.objects.get_current()
        return self.get(sites__id=site.id,
                        provider=provider)


@python_2_unicode_compatible
class SocialApp(models.Model):
    objects = SocialAppManager()

    provider = models.CharField(max_length=30,
                                choices=providers.registry.as_choices())
    name = models.CharField(max_length=40)
    client_id = models.CharField(max_length=100,
                                 help_text='App ID, or consumer key')
    secret = models.CharField(max_length=100,
                              help_text='API secret, client secret, or'
                              ' consumer secret')
    key = models.CharField(max_length=100,
                           blank=True,
                           help_text='Key (Stack Exchange only)')
    # Most apps can be used across multiple domains, therefore we use
    # a ManyToManyField. Note that Facebook requires an app per domain
    # (unless the domains share a common base name).
    # blank=True allows for disabling apps without removing them
    sites = models.ManyToManyField(Site, blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class SocialAccount(models.Model):
    user = models.ForeignKey(allauth.app_settings.USER_MODEL)
    provider = models.CharField(max_length=30,
                                choices=providers.registry.as_choices())
    # Just in case you're wondering if an OpenID identity URL is going
    # to fit in a 'uid':
    #
    # Ideally, URLField(max_length=1024, unique=True) would be used
    # for identity.  However, MySQL has a max_length limitation of 255
    # for URLField. How about models.TextField(unique=True) then?
    # Well, that won't work either for MySQL due to another bug[1]. So
    # the only way out would be to drop the unique constraint, or
    # switch to shorter identity URLs. Opted for the latter, as [2]
    # suggests that identity URLs are supposed to be short anyway, at
    # least for the old spec.
    #
    # [1] http://code.djangoproject.com/ticket/2495.
    # [2] http://openid.net/specs/openid-authentication-1_1.html#limits

    uid = models.CharField(max_length=255)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    extra_data = JSONField(default='{}')

    class Meta:
        unique_together = ('provider', 'uid')

    def authenticate(self):
        return authenticate(account=self)

    def __str__(self):
        return force_text(self.user)

    def get_profile_url(self):
        return self.get_provider_account().get_profile_url()

    def get_avatar_url(self):
        return self.get_provider_account().get_avatar_url()

    def get_provider(self):
        return providers.registry.by_id(self.provider)

    def get_provider_account(self):
        return self.get_provider().wrap_account(self)


@python_2_unicode_compatible
class SocialToken(models.Model):
    app = models.ForeignKey(SocialApp)
    account = models.ForeignKey(SocialAccount)
    token = models \
        .TextField(help_text='"oauth_token" (OAuth1) or access token (OAuth2)')
    token_secret = models \
        .TextField(blank=True,
                   help_text='"oauth_token_secret" (OAuth1) or refresh'
                   ' token (OAuth2)')
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('app', 'account')

    def __str__(self):
        return self.token


class SocialLogin(object):
    """
    Represents a social user that is in the process of being logged
    in. This consists of the following information:

    `account` (`SocialAccount` instance): The social account being
    logged in. Providers are not responsible for checking whether or
    not an account already exists or not. Therefore, a provider
    typically creates a new (unsaved) `SocialAccount` instance. The
    `User` instance pointed to by the account (`account.user`) may be
    prefilled by the provider for use as a starting point later on
    during the signup process.

    `token` (`SocialToken` instance): An optional access token token
    that results from performing a successful authentication
    handshake.

    `state` (`dict`): The state to be preserved during the
    authentication handshake. Note that this state may end up in the
    url -- do not put any secrets in here. It currently only contains
    the url to redirect to after login.

    `email_addresses` (list of `EmailAddress`): Optional list of
    e-mail addresses retrieved from the provider.
    """

    def __init__(self, account=None, token=None, email_addresses=[]):
        if token:
            assert token.account is None or token.account == account
            token.account = account
        self.token = token
        self.account = account
        self.email_addresses = email_addresses
        self.state = {}

    def connect(self, request, user):
        self.account.user = user
        self.save(request, connect=True)

    def serialize(self):
        ret = dict(account=serialize_instance(self.account),
                   user=serialize_instance(self.account.user),
                   state=self.state,
                   email_addresses=[serialize_instance(ea)
                                    for ea in self.email_addresses])
        if self.token:
            ret['token'] = serialize_instance(self.token)
        return ret

    @classmethod
    def deserialize(cls, data):
        account = deserialize_instance(SocialAccount, data['account'])
        user = deserialize_instance(get_user_model(), data['user'])
        account.user = user
        if 'token' in data:
            token = deserialize_instance(SocialToken, data['token'])
        else:
            token = None
        email_addresses = []
        for ea in data['email_addresses']:
            email_address = deserialize_instance(EmailAddress, ea)
            email_addresses.append(email_address)
        ret = SocialLogin()
        ret.token = token
        ret.account = account
        ret.user = user
        ret.email_addresses = email_addresses
        ret.state = data['state']
        return ret

    def save(self, request, connect=False):
        """
        Saves a new account. Note that while the account is new,
        the user may be an existing one (when connecting accounts)
        """
        assert not self.is_existing
        user = self.account.user
        user.save()
        self.account.user = user
        self.account.save()
        if self.token:
            self.token.account = self.account
            self.token.save()
        if connect:
            # TODO: Add any new email addresses automatically?
            pass
        else:
            setup_user_email(request, user, self.email_addresses)

    @property
    def is_existing(self):
        """
        Account is temporary, not yet backed by a database record.
        """
        return self.account.pk

    def lookup(self):
        """
        Lookup existing account, if any.
        """
        assert not self.is_existing
        try:
            a = SocialAccount.objects.get(provider=self.account.provider,
                                          uid=self.account.uid)
            # Update account
            a.extra_data = self.account.extra_data
            self.account = a
            a.save()
            # Update token
            if self.token:
                assert not self.token.pk
                try:
                    t = SocialToken.objects.get(account=self.account,
                                                app=self.token.app)
                    t.token = self.token.token
                    if self.token.token_secret:
                        # only update the refresh token if we got one
                        # many oauth2 providers do not resend the refresh token
                        t.token_secret = self.token.token_secret
                    t.expires_at = self.token.expires_at
                    t.save()
                    self.token = t
                except SocialToken.DoesNotExist:
                    self.token.account = a
                    self.token.save()
        except SocialAccount.DoesNotExist:
            pass

    def get_redirect_url(self, request):
        url = self.state.get('next')
        return url

    @classmethod
    def state_from_request(cls, request):
        state = {}
        next_url = get_next_redirect_url(request)
        if next_url:
            state['next'] = next_url
        state['process'] = request.REQUEST.get('process', 'login')
        return state

    @classmethod
    def stash_state(cls, request):
        state = cls.state_from_request(request)
        verifier = get_random_string()
        request.session['socialaccount_state'] = (state, verifier)
        return verifier

    @classmethod
    def unstash_state(cls, request):
        if 'socialaccount_state' not in request.session:
            raise PermissionDenied()
        state, verifier = request.session.pop('socialaccount_state')
        return state

    @classmethod
    def verify_and_unstash_state(cls, request, verifier):
        if 'socialaccount_state' not in request.session:
            raise PermissionDenied()
        state, verifier2 = request.session.pop('socialaccount_state')
        if verifier != verifier2:
            raise PermissionDenied()
        return state
