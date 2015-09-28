#===============================================================================
# Support for Reddit Oauth2 authentication
# Author: Wendy Edwards (wayward710)
#===============================================================================
from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class RedditOAuth2Account(ProviderAccount):
    pass

class RedditOAuth2Provider(OAuth2Provider):
    id = 'reddit_oauth2'
    name = 'Reddit'
    package = 'allauth.socialaccount.providers.reddit_oauth2'
    account_class = RedditOAuth2Account

    def extract_uid(self, data):
        return data['name']

    def extract_common_fields(self, data):
        return dict(name=data.get('name'))
        
    def get_default_scope(self):
        scope = ['identity']
        return scope        

providers.registry.register(RedditOAuth2Provider)
