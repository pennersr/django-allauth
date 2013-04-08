from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

class VimeoAccount(ProviderAccount):
    pass


class VimeoProvider(OAuthProvider):
    id = 'vimeo'
    name = 'Vimeo'
    package = 'allauth.socialaccount.providers.vimeo'
    account_class = VimeoAccount

    def get_default_scope(self):
        scope = []
        return scope

providers.registry.register(VimeoProvider)
