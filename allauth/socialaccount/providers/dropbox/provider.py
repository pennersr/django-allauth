from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

class DropboxAccount(ProviderAccount):
    pass


class DropboxProvider(OAuthProvider):
    id = 'dropbox'
    name = 'Dropbox'
    package = 'allauth.socialaccount.providers.dropbox'
    account_class = DropboxAccount


providers.registry.register(DropboxProvider)
