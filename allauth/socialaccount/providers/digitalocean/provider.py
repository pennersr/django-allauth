from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.digitalocean.views import (
    DigitalOceanOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DigitalOceanAccount(ProviderAccount):
    def to_str(self):
        dflt = super().to_str()
        return self.account.extra_data.get("account", {}).get("email") or dflt


class DigitalOceanProvider(OAuth2Provider):
    id = "digitalocean"
    name = "DigitalOcean"
    account_class = DigitalOceanAccount
    oauth2_adapter_class = DigitalOceanOAuth2Adapter

    def extract_uid(self, data):
        return str(data["account"]["uuid"])

    def extract_common_fields(self, data):
        return dict(email=data["account"]["email"])


provider_classes = [DigitalOceanProvider]
