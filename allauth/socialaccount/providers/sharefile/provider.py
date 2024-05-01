from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.sharefile.views import (
    ShareFileOAuth2Adapter,
)


class ShareFileAccount(ProviderAccount):
    def to_str(self):
        dflt = super(ShareFileAccount, self).to_str()
        return self.account.extra_data.get("name", dflt)


class ShareFileProvider(OAuth2Provider):
    id = "sharefile"
    name = "ShareFile"
    account_class = ShareFileAccount
    oauth2_adapter_class = ShareFileOAuth2Adapter

    def extract_uid(self, data):
        return str(data.get("Id", ""))

    def extract_common_fields(self, data):
        return dict(
            email=data.get("Email", ""),
            username=data.get("Username", ""),
            name=data.get("FullName", ""),
        )


provider_classes = [ShareFileProvider]
