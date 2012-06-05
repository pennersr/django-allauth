from allauth.socialaccount.providers import register_provider
from allauth.socialaccount.providers.base import Provider


class GitHubProvider(Provider):
    id = 'github'
    package = 'allauth.socialaccount.providers.github'

register_provider(GitHubProvider)
