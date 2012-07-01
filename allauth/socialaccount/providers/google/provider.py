from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.app_settings import QUERY_EMAIL

class Scope:
    USERINFO_PROFILE = 'https://www.googleapis.com/auth/userinfo.profile'
    USERINFO_EMAIL = 'https://www.googleapis.com/auth/userinfo.email'


class GoogleAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def __unicode__(self):
        dflt = super(GoogleAccount, self).__unicode__()
        return self.account.extra_data.get('name', dflt)


class GoogleProvider(OAuth2Provider):
    id = 'google'
    name = 'Google'
    package = 'allauth.socialaccount.providers.google'
    account_class = GoogleAccount

    def get_default_scope(self):
        scope = [Scope.USERINFO_PROFILE]
        if QUERY_EMAIL:
            scope.append(Scope.USERINFO_EMAIL)
        return scope

providers.registry.register(GoogleProvider)
