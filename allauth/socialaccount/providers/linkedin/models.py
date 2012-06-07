from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount


class LinkedInAccount(ProviderAccount):
    pass


class LinkedInProvider(Provider):
    id = 'linkedin'
    name = 'LinkedIn'
    package = 'allauth.socialaccount.providers.linkedin'
    account_class = LinkedInAccount

providers.registry.register(LinkedInProvider)
