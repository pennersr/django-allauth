from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.fxa.constants import PROVIDER_ID
from allauth.socialaccount.providers.fxa.views import (
    FirefoxAccountsOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FirefoxAccountsAccount(ProviderAccount):
    def to_str(self):
        return self.account.uid


class FirefoxAccountsProvider(OAuth2Provider):
    id = PROVIDER_ID
    name = "Firefox Accounts"
    account_class = FirefoxAccountsAccount
    oauth2_adapter_class = FirefoxAccountsOAuth2Adapter

    def get_default_scope(self):
        return ["profile"]

    def extract_uid(self, data):
        return str(data["uid"])

    def extract_common_fields(self, data):
        return dict(email=data.get("email"))


provider_classes = [FirefoxAccountsProvider]
