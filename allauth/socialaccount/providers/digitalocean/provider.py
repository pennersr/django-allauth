from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.digitalocean.views import (
    DigitalOceanOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DigitalOceanAccount(ProviderAccount):
    pass


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
