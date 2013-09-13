from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class SoundCloudAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('permalink_url')

    def get_avatar_url(self):
        return self.account.extra_data.get('avatar_url')

    def to_str(self):
        dflt = super(SoundCloudAccount, self).to_str()
        full_name = self.account.extra_data.get('full_name')
        username = self.account.extra_data.get('username')
        return full_name or username or dflt


class SoundCloudProvider(OAuth2Provider):
    id = 'soundcloud'
    name = 'SoundCloud'
    package = 'allauth.socialaccount.providers.soundcloud'
    account_class = SoundCloudAccount


    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(name=data.get('full_name'),
                    username=data.get('username'),
                    email=data.get('email'))


providers.registry.register(SoundCloudProvider)
