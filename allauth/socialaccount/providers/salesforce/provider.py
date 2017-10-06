from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SalesforceAccount(ProviderAccount):
    pass


class SalesforceProvider(OAuth2Provider):
    id = 'salesforce'
    name = 'Salesforce'
    account_class = SalesforceAccount

    def get_default_scope(self):
        return ['id', 'full', 'refresh_token']

    def extract_uid(self, userinfo):
        return userinfo['user_id']


provider_classes = [SalesforceProvider]
