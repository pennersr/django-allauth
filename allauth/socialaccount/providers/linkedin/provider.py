from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider

class LinkedInAccount(ProviderAccount):
    pass


class LinkedInProvider(OAuthProvider):
    id = 'linkedin'
    name = 'LinkedIn'
    package = 'allauth.socialaccount.providers.linkedin'
    account_class = LinkedInAccount

providers.registry.register(LinkedInProvider)
