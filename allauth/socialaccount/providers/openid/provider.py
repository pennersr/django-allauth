try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount

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
        for d, p in provider_map.items():
            if domain.lower().find(d) >= 0:
                ret = p
                break
        return ret

    def to_str(self):
        return self.account.uid


class OpenIDProvider(Provider):
    id = 'openid'
    name = 'OpenID'
    package = 'allauth.socialaccount.providers.openid'
    account_class = OpenIDAccount

    def get_login_url(self, request, **kwargs):
        url = reverse('openid_login')
        if kwargs:
            url += '?' + urlencode(kwargs)
        return url

    def get_brands(self):
        # These defaults are a bit too arbitrary...
        default_servers = [dict(id='yahoo',
                                name='Yahoo',
                                openid_url='http://me.yahoo.com'),
                           dict(id='hyves',
                                name='Hyves',
                                openid_url='http://hyves.nl')]
        return self.get_settings().get('SERVERS', default_servers)
        

providers.registry.register(OpenIDProvider)
