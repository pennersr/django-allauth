from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils import simplejson

import allauth.app_settings
from allauth.utils import get_login_redirect_url

import providers
from fields import JSONField


class SocialAppManager(models.Manager):
    def get_current(self, provider):
        site = Site.objects.get_current()
        return self.get(site=site,
                        provider=provider)


class SocialApp(models.Model):
    objects = SocialAppManager()

    site = models.ForeignKey(Site)
    provider = models.CharField(max_length=30, 
                                choices=providers.registry.as_choices())
    name = models.CharField(max_length=40)
    key = models.CharField(max_length=100,
                           help_text='App ID, or consumer key')
    secret = models.CharField(max_length=100,
                              help_text='API secret, or consumer secret')

    def __unicode__(self):
        return self.name

class SocialAccount(models.Model):
    user = models.ForeignKey(User)
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

    def __unicode__(self):
        return unicode(self.user)

    def get_profile_url(self):
        return self.get_provider_account().get_profile_url()

    def get_avatar_url(self):
        return self.get_provider_account().get_avatar_url()

    def get_provider(self):
        return providers.registry.by_id(self.provider)

    def get_provider_account(self):
        return self.get_provider().wrap_account(self)


class SocialToken(models.Model):
    app = models.ForeignKey(SocialApp)
    account = models.ForeignKey(SocialAccount)
    token = models.CharField(max_length=200)
    token_secret = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('app', 'account')

    def __unicode__(self):
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
    url (e.g. OAuth2 `state` parameter) -- do not put any secrets in
    there. It currently only contains the url to redirect to after
    login.
    """

    def __init__(self, account, token=None):
        if token:
            assert token.account is None or token.account == account
            token.account = account
        self.token = token
        self.account = account
        self.state = {}

    def save(self):
        user = self.account.user
        user.save()
        self.account.user = user
        self.account.save()
        if self.token:
            self.token.account = self.account
            self.token.save()

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
                    t.token_secret = self.token.token_secret
                    t.save()
                    self.token = t
                except SocialToken.DoesNotExist:
                    self.token.account = a
                    self.token.save()
        except SocialAccount.DoesNotExist:
            pass
    
    def get_redirect_url(self, 
                         fallback=allauth.app_settings.LOGIN_REDIRECT_URL):
        url = self.state.get('next') or fallback
        return url
            
    @classmethod
    def state_from_request(cls, request):
        state = {}
        next = get_login_redirect_url(request, fallback=None)
        if next:
            state['next'] = next
        return state

    @classmethod
    def marshall_state(cls, request):
        state = cls.state_from_request(request)
        return simplejson.dumps(state)
    
    @classmethod
    def unmarshall_state(cls, state_string):
        if state_string:
            state = simplejson.loads(state_string)
        else:
            state = {}
        return state
    
            
