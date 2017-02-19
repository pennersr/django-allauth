from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class OnedriveOAuth2Account(ProviderAccount):
    pass


class OnedriveOAuth2Provider(OAuth2Provider):
    id = 'onedrive'
    name = 'Onedrive'
    account_class = OnedriveOAuth2Account

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'),
                    email=data.get('email'))


providers.registry.register(OnedriveOAuth2Provider)
