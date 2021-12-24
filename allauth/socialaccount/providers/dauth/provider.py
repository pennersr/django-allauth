from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DAuthAccount(ProviderAccount):
    pass


class DAuthProvider(OAuth2Provider):
    id = 'dauth'
    name = 'DAuth'
    account_class = DAuthAccount

    def extract_uid(self, data):
        return str(data['id'])

    def extract_common_fields(self, data):
        return dict(email=data.get('email'),
                    name=data.get('name'),
                    gender=data.get('gender'),
                    phoneNumber=data.get('phoneNumber'))

    def get_default_scope(self):
        scope = ['user', 'openid', 'email', 'profile']
        return scope


providers.registry.register(DAuthProvider)
