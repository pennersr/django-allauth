from urlparse import urlparse
from django.db import models
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

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
    def get_brand(self):
        ret = super(OpenIDAccount, self).get_brand()
        domain = urlparse(self.account.uid).netloc
        # FIXME: Instead of hardcoding, derive this from the domains
        # listed in the openid endpoints setting.
        provider_map = {'yahoo': dict(id='yahoo',
                                      name='Yahoo'),
                         'hyves': dict(id='hyves',
                                       name='Hyves'),
                         'google': dict(id='google',
                                        name='Google')}
        for d, p in provider_map.iteritems():
            if domain.lower().find(d) >= 0:
                ret = p
                break
        return ret

    def __unicode__(self):
        return self.account.uid


class OpenIDProvider(Provider):
    id = 'openid'
    name = 'OpenID'
    package = 'allauth.socialaccount.providers.openid'
    account_class = OpenIDAccount

    def get_login_url(self, request, next=None, openid=None):
        url = reverse('openid_login')
        query = {}
        if openid:
            query['openid'] = openid
        if next:
            query['next'] = next
        if query:
            url += '?' + urlencode(query)
        return url

    def get_brands(self):
        return self.get_settings()['SERVERS']
        

providers.registry.register(OpenIDProvider)
