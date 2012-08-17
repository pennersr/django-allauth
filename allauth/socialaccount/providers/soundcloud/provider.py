from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider 


class SoundCloudAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('permalink_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def __unicode__(self):
        dflt = super(SoundCloudAccount, self).__unicode__()
        full_name = self.account.extra_data.get('full_name')
        username = self.account.extra_data.get('username')
        return full_name or username or dflt

class SoundCloudProvider(OAuth2Provider):
    id = 'soundcloud'
    name = 'SoundCloud'
    package = 'allauth.socialaccount.providers.soundcloud'
    account_class = SoundCloudAccount

        
providers.registry.register(SoundCloudProvider)
