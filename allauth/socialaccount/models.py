from urlparse import urlparse
from django.db import models
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from defs import Provider, PROVIDER_CHOICES
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
                                choices=PROVIDER_CHOICES)
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
                                choices=PROVIDER_CHOICES)
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
        # FIXME: To be encapsulated in a per provider class
        if self.provider == Provider.TWITTER.id:
            screen_name = self.extra_data.get('screen_name')
            return 'http://twitter.com/' + screen_name
        elif self.provider == Provider.FACEBOOK.id:
            return self.extra_data.get('link')
        else:
            raise NotImplementedError
    
    def get_avatar_url(self):
        ret = None
        # FIXME: To be encapsulated in a per provider class
        if self.provider == Provider.TWITTER.id:
            profile_image_url = self.extra_data.get('profile_image_url')
            if profile_image_url:
                # Hmm, hack to get our hands on the large image.  Not
                # really documented, but seems to work.
                ret = profile_image_url.replace('_normal', '') 
        elif self.provider == Provider.FACEBOOK.id:
            ret = 'http://graph.facebook.com/%s/picture?type=large' % self.uid
        return ret

    def get_provider(self):
        # FIXME: to be refactored when provider classes are introduced
        ret = self.provider
        if ret == Provider.OPENID.id:
            domain = urlparse(self.uid).netloc
            provider_map = {'yahoo': Provider.YAHOO,
                            'google': Provider.GOOGLE}
            for d,p in provider_map.iteritems():
                if domain.lower().find(d) >= 0:
                    ret = p
                    break
        return ret

    def get_provider_account(self):
        # FIXME: To be refactored
        return self

    def sync(self, data):
        # FIXME: to be refactored when provider classes are introduced
        if self.provider == Provider.FACEBOOK.id:
            self.extra_data = { 'link': data['facebook_me']['link'],
                                'name': data['facebook_me']['name'] }
            self.save()
            access_token = data['facebook_access_token']
            token, created = SocialToken.objects \
                .get_or_create(app=SocialApp.objects.get_current(Provider.FACEBOOK.id),
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

