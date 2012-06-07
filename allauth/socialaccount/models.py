from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

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
    provider = models.CharField(max_length=30, choices=providers.registry.as_choices())
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

    def sync(self, data):
        # FIXME: to be refactored when provider classes are introduced
        if self.provider == 'facebook':
            self.extra_data = {'link': data['facebook_me']['link'], 'name': data['facebook_me']['name']}
            self.save()
            access_token = data['facebook_access_token']
            token, created = SocialToken.objects \
                .get_or_create(app=SocialApp.objects.get_current('facebook'),
                               account=self,
                               defaults={'token': access_token})
            if not created and token.token != access_token:
                token.token = access_token
                token.save()
        else:
            self.save()


class SocialToken(models.Model):
    app = models.ForeignKey(SocialApp)
    account = models.ForeignKey(SocialAccount)
    token = models.CharField(max_length=200)
    token_secret = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('app', 'account')

    def __unicode__(self):
        return self.token
