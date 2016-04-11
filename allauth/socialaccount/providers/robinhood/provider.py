from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class RobinhoodAccount(ProviderAccount):
    def get_avatar_url(self):
        return None

    def to_str(self):
        return self.account.extra_data.get(
            'username',
            super(RobinhoodAccount, self).to_str())


class RobinhoodProvider(OAuth2Provider):
    id = 'robinhood'
    name = 'Robinhood'
    account_class = RobinhoodAccount

    def get_default_scope(self):
        return ['read']

    def extract_uid(self, data):
        return data['id']

    def extract_common_fields(self, data):
        return dict(username=data.get('username'))

providers.registry.register(RobinhoodProvider)
