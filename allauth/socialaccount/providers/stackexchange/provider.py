from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.models import SocialToken

class StackExchangeAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('items')[0].get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('items')[0].get('profile_image')

    def __unicode__(self):
        dflt = super(StackExchangeAccount, self).__unicode__()
        try:
            return self.account.extra_data.get('items')[0].get('display_name')
        except (KeyError, IndexError):
            return dflt

    def get_brand(self):
        token = SocialToken.objects.get(account = self.account)
        return dict(id=token.app.id,
                    name=token.app.name)

class StackExchangeProvider(OAuth2Provider):
    id = 'stackexchange'
    name = 'StackExchange'
    package = 'allauth.socialaccount.providers.stackexchange'
    account_class = StackExchangeAccount

    def get_default_scope(self):
        scope = ['read_inbox', 'write_access', 'private_info']
        return scope

providers.registry.register(StackExchangeProvider)
