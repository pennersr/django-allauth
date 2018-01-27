from django.urls import reverse
from django.utils.http import urlencode

from allauth.compat import urlparse
from allauth.socialaccount.providers.base import Provider, ProviderAccount

from .utils import (
    AXAttribute,
    OldAXAttribute,
    SRegField,
    get_email_from_response,
    get_value_from_response,
)


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

    def get_server_settings(self, endpoint):
        servers = self.get_settings().get('SERVERS', [])
        for server in servers:
            if endpoint == server.get('openid_url'):
                return server
        return {}

    def extract_extra_data(self, response):
        extra_data = {}
        server_settings = \
            self.get_server_settings(response.endpoint.server_url)
        extra_attributes = server_settings.get('extra_attributes', [])
        for attribute_id, name, _ in extra_attributes:
            extra_data[attribute_id] \
                = get_value_from_response(response, ax_names=[name])
        return extra_data

    def extract_uid(self, response):
        return response.identity_url

    def extract_common_fields(self, response):
        first_name = get_value_from_response(response,
                                             ax_names=[AXAttribute
                                                       .PERSON_FIRST_NAME,
                                                       OldAXAttribute
                                                       .PERSON_FIRST_NAME]) \
            or ''
        last_name = get_value_from_response(response,
                                            ax_names=[AXAttribute
                                                      .PERSON_LAST_NAME,
                                                      OldAXAttribute
                                                      .PERSON_LAST_NAME]) \
            or ''
        name = get_value_from_response(response,
                                       sreg_names=[SRegField.NAME],
                                       ax_names=[AXAttribute.PERSON_NAME,
                                                 OldAXAttribute.PERSON_NAME]) \
            or ''
        return dict(email=get_email_from_response(response),
                    first_name=first_name,
                    last_name=last_name, name=name)


provider_classes = [OpenIDProvider]
