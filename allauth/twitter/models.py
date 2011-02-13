from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from allauth.socialaccount.defs import SocialAccountProvider
from allauth.socialaccount.models import SocialAccount

class TwitterAppManager(models.Manager):
    def get_current(self):
        site = Site.objects.get_current()
        return self.get(site=site)

class TwitterApp(models.Model):
    objects = TwitterAppManager()

    site = models.ForeignKey(Site)
    name = models.CharField(max_length=40)
    consumer_key = models.CharField(max_length=80)
    consumer_secret = models.CharField(max_length=80)
    request_token_url = models.URLField(verify_exists=False)
    access_token_url = models.URLField(verify_exists=False)
    authorize_url = models.URLField(verify_exists=False)

    def __unicode__(self):
        return u"%s (@%s)" % (self.name, self.site)

class TwitterAccount(SocialAccount):
    social_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=15)
    profile_image_url = models.URLField()

    def get_profile_url(self):
        return 'http://twitter.com/' + self.username

    def get_avatar_url(self):
        ret = None
        if self.profile_image_url:
            # Hmm, hack to get our hands on the large image.  Not
            # really documented, but seems to work.
            ret = self.profile_image_url.replace('_normal', '') 
        return ret

    def get_provider(self):
        return SocialAccountProvider.TWITTER

    def __unicode__(self):
        return self.username
