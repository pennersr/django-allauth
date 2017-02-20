from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DropboxOAuth2Account(ProviderAccount):
    pass


class DropboxOAuth2Provider(OAuth2Provider):
    id = 'dropbox_oauth2'
    name = 'Dropbox'
    account_class = DropboxOAuth2Account

    def extract_uid(self, data):
        return data['uid']

    def extract_common_fields(self, data):
        return dict(name=data.get('display_name'),
                    email=data.get('email'))


providers.registry.register(DropboxOAuth2Provider)
