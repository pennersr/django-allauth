from django.db import models

from allauth.socialaccount.providers import register_provider
from allauth.socialaccount.providers.base import Provider

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


class OpenIDProvider(Provider):
    id = 'openid'
    package = 'allauth.socialaccount.providers.openid'

register_provider(OpenIDProvider)
