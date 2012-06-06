from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount


class GitHubAccount(ProviderAccount):
    pass

class GitHubProvider(Provider):
    id = 'github'
    package = 'allauth.socialaccount.providers.github'
    account_class = GitHubAccount

providers.registry.register_provider(GitHubProvider)
