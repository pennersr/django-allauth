from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DiscordAccount(ProviderAccount):
    def to_str(self):
        dflt = super(DiscordAccount, self).to_str()
        return self.account.extra_data.get('username', dflt)

    def get_avatar_url(self):
        if ('id' in self.account.extra_data.keys()
                and 'avatar' in self.account.extra_data.keys()):
            return 'https://cdn.discordapp.com/avatars/{id}/{avatar}.png'\
                .format(**self.account.extra_data)


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

    def extract_email_addresses(self, data):
        ret = []
        email = data.get('email')
        if email and data.get('verified'):
            ret.append(EmailAddress(email=email,
                       verified=True,
                       primary=True))
        return ret


provider_classes = [DiscordProvider]
