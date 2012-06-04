from allauth.socialaccount.providers import register_provider
from allauth.socialaccount.providers.base import Provider


class FacebookProvider(Provider):
    id = 'facebook'
    package = 'allauth.socialaccount.providers.facebook'

register_provider(FacebookProvider)
