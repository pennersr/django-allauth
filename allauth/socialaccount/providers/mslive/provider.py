from __future__ import unicode_literals

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MSLiveAccount(ProviderAccount):
#    def get_avatar_url(self):
#        return self.account.extra_data.get('picture')

    def to_str(self):
        name = '{0} {1}'.format(self.account.extra_data.get('first_name', ''),
                                self.account.extra_data.get('last_name', ''))
        if name.strip() != '':
            return name
        return super(MSLiveAccount, self).to_str()


class MSLiveProvider(OAuth2Provider):
    id = str('mslive')
    name = 'MSLive'
    package = 'allauth.socialaccount.providers.mslive'
    account_class = MSLiveAccount

# doc on scopes available
#http://msdn.microsoft.com/en-us/library/live/hh243646.aspx 
    def get_default_scope(self):
        return ['wl.basic', 'wl.emails']

    def extract_uid(self, data):
        print "extract_uid data"
        print data
        return str(data['id'])

    def extract_common_fields(self, data):
        try:
            email = data.get('emails').get('preferred')
        except:
            email = None

        return dict(email=email,
                    last_name=data.get('last_name'),
                    first_name=data.get('first_name'))


providers.registry.register(MSLiveProvider)
