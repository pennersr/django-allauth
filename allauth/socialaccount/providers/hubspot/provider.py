from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    oauth2 = 'oauth'


class HubSpotAccount(ProviderAccount):
    pass


class HubSpotProvider(OAuth2Provider):
    id = 'hubspot'
    name = 'HubSpot'
    account_class = HubSpotAccount

    def get_default_scope(self):
        scope = [Scope.oauth2]
        return scope

    def extract_uid(self, data):
        return str(data['user_id'])

    def extract_common_fields(self, data):
        return dict(username=data.get('user'))


provider_classes = [HubSpotProvider]
