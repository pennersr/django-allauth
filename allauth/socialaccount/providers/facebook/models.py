from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import Provider, ProviderAccount

class FacebookAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        uid = self.account.uid
        return 'http://graph.facebook.com/%s/picture?type=large' % uid
    
class FacebookProvider(Provider):
    id = 'facebook'
    package = 'allauth.socialaccount.providers.facebook'
    account_class = FacebookAccount

providers.registry.register_provider(FacebookProvider)
