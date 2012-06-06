from django.db import models

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount

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

class OpenIDAccount(ProviderAccount):
    pass

class OpenIDProvider(Provider):
    id = 'openid'
    package = 'allauth.socialaccount.providers.openid'
    account_class = ProviderAccount

providers.registry.register_provider(OpenIDProvider)
