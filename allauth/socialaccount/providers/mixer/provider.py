from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class MixerAccount(ProviderAccount):
    def _get_token(self):
        return self.account.extra_data.get('channel', {}).get('token')

    def get_profile_url(self):
        return 'https://mixer.com/' + self._get_token()

    def get_avatar_url(self):
        return self.account.extra_data.get('avatarUrl')

    def to_str(self):
        return self._get_token()


class MixerProvider(OAuth2Provider):
    id = 'mixer'
    name = 'Mixer'
    account_class = MixerAccount

    def get_default_scope(self):
        return ['user:details:self']

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return {
            'username': data.get('username'),
            'email': data.get('email'),
        }


provider_classes = [MixerProvider]
