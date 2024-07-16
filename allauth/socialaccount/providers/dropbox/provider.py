from allauth.socialaccount import providers
from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.dropbox.views import DropboxOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DropboxOAuth2Account(ProviderAccount):
    pass


class DropboxOAuth2Provider(OAuth2Provider):
    id = "dropbox"
    name = "Dropbox"
    account_class = DropboxOAuth2Account
    oauth2_adapter_class = DropboxOAuth2Adapter

    def extract_uid(self, data):
        return data["account_id"]

    def extract_common_fields(self, data):
        return dict(name=data["name"]["display_name"], email=data["email"])


providers.registry.register(DropboxOAuth2Provider)
