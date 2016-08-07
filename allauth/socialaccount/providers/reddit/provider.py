from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class RedditAccount(ProviderAccount):
    pass


class RedditProvider(OAuth2Provider):
    id = 'reddit'
    name = 'Reddit'
    account_class = RedditAccount

    def extract_uid(self, data):
        return data['name']

    def extract_common_fields(self, data):
        return dict(name=data.get('name'))

    def get_default_scope(self):
        scope = ['identity']
        return scope

providers.registry.register(RedditProvider)
