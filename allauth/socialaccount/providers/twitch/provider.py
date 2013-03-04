from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class TwitchAccount(ProviderAccount):
    def get_profile_url(self):
        return 'http://twitch.tv/' + self.account.extra_data.get('name') 

    def get_avatar_url(self):
        return self.account.extra_data.get('logo')

    def __unicode__(self):
        dflt = super(TwitchAccount, self).__unicode__()
        return self.account.extra_data.get('name', dflt)


class TwitchProvider(OAuth2Provider):
    id = 'twitch'
    name = 'Twitch'
    package = 'allauth.socialaccount.providers.twitch'
    account_class = TwitchAccount

providers.registry.register(TwitchProvider)
