from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DiscordAccount(ProviderAccount):
    def to_str(self):
        dflt = super(DiscordAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)


class DiscordProvider(OAuth2Provider):
    id = 'discord'
    name = 'Discord'
    account_class = DiscordAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(
            email=data.get('email'),
            username=data.get('username'),
            name=data.get('username'),
        )

    def get_default_scope(self):
        return ['email', 'identify']


providers.registry.register(DiscordProvider)
