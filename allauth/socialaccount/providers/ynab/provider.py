from allauth.socialaccount.providers.base import AuthAction, ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class Scope(object):
    ACCESS = 'read-only'


class YNABAccount(ProviderAccount):
    pass


class YNABProvider(OAuth2Provider):
    id = 'ynab'
    name = 'YNAB'
    account_class = YNABAccount

    def get_default_scope(self):
        scope = [Scope.ACCESS]
        return scope

    def get_auth_params(self, request, action):
        ret = super(YNABProvider, self).get_auth_params(request,
                                                        action)
        if action == AuthAction.REAUTHENTICATE:
            ret['prompt'] = 'select_account consent'
        return ret

    def extract_uid(self, data):
        return str(data['data']['user']['id'])


provider_classes = [YNABProvider]
