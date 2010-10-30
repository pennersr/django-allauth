from urlparse import urlparse
from django.db import models
from allauth.socialaccount.defs import SocialAccountProvider
from allauth.socialaccount.models import SocialAccount

class OpenIDAccount(SocialAccount):
    # Ideally, URLField(max_length=1024, unique=True) would be used
    # for identity.  However, MySQL has a max_length limitation of 255
    # for URLField. So let's be pragmetic and switch to TextField...
    # TODO: Model field validation to ensure valid URLs
    identity = models.TextField(unique=True)
    
    def __unicode__(self):
        return self.identity

    def get_provider(self):
        ret = SocialAccountProvider.OPENID
        domain = urlparse(self.identity).netloc
        provider_map = {'yahoo': SocialAccountProvider.YAHOO,
                        'google': SocialAccountProvider.GOOGLE}
        for d,p in provider_map.iteritems():
            if domain.lower().find(d) >= 0:
                ret = p
                break
        return ret

class OpenIDStore(models.Model):
    server_url = models.CharField(max_length=255)
    handle = models.CharField(max_length=255)
    secret = models.TextField()
    issued = models.IntegerField()
    lifetime = models.IntegerField()
    assoc_type = models.TextField()

    def __unicode__(self):
        return self.server_url

class OpenIDNonce(models.Model):
    server_url = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    salt = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.server_url

