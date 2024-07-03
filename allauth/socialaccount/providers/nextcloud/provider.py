from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.nextcloud.views import (
    NextCloudOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class NextCloudAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get("id") or super().to_str()


class NextCloudProvider(OAuth2Provider):
    id = "nextcloud"
    name = "NextCloud"
    account_class = NextCloudAccount
    oauth2_adapter_class = NextCloudOAuth2Adapter

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(
            username=data["displayname"],
            email=data["email"],
        )

    def get_default_scope(self):
        scope = ["read"]
        return scope


provider_classes = [NextCloudProvider]
