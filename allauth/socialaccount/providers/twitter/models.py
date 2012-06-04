from allauth.socialaccount.providers import register_provider
from allauth.socialaccount.providers.base import Provider


class TwitterProvider(Provider):
    id = 'twitter'
    package = 'allauth.socialaccount.providers.twitter'

register_provider(TwitterProvider)
