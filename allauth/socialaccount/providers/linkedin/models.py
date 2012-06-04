from allauth.socialaccount.providers import register_provider
from allauth.socialaccount.providers.base import Provider


class LinkedInProvider(Provider):
    id = 'linkedin'
    package = 'allauth.socialaccount.providers.linkedin'

register_provider(LinkedInProvider)
