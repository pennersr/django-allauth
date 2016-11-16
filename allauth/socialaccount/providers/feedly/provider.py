from __future__ import unicode_literals

from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FeedlyAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        name = '{0} {1}'.format(self.account.extra_data.get('givenName', ''),
                                self.account.extra_data.get('familyName', ''))
        if name.strip() != '':
            return name
        return super(FeedlyAccount, self).to_str()


class FeedlyProvider(OAuth2Provider):
    id = str('feedly')
    name = 'Feedly'
    account_class = FeedlyAccount

    def get_default_scope(self):
        return ['https://cloud.feedly.com/subscriptions']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    last_name=data.get('familyName'),
                    first_name=data.get('givenName'))


providers.registry.register(FeedlyProvider)
