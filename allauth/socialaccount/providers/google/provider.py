from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import (ProviderAccount,
                                                  AuthAction)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.app_settings import QUERY_EMAIL


class Scope(object):
    USERINFO_PROFILE = 'https://www.googleapis.com/auth/userinfo.profile'
    USERINFO_EMAIL = 'https://www.googleapis.com/auth/userinfo.email'


class GoogleAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get('link')

    def get_avatar_url(self):
        return self.account.extra_data.get('picture')

    def to_str(self):
        dflt = super(GoogleAccount, self).to_str()
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

    def get_auth_params(self, request, action):
        ret = super(GoogleProvider, self).get_auth_params(request,
                                                          action)
        if action == AuthAction.REAUTHENTICATE:
            ret['approval_prompt'] = 'force'
        return ret

providers.registry.register(GoogleProvider)
