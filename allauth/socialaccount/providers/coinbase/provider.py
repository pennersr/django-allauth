from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.coinbase.views import (
    CoinbaseOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class CoinbaseAccount(ProviderAccount):
    def get_avatar_url(self):
        return None

    def to_str(self):
        return self.account.extra_data.get(
            "name", super(CoinbaseAccount, self).to_str()
        )


class CoinbaseProvider(OAuth2Provider):
    id = "coinbase"
    name = "Coinbase"
    account_class = CoinbaseAccount
    oauth2_adapter_class = CoinbaseOAuth2Adapter

    def get_default_scope(self):
        # See: https://coinbase.com/docs/api/permissions
        return ["wallet:user:email"]

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        # See: https://coinbase.com/api/doc/1.0/users/index.html
        return dict(email=data["email"])


provider_classes = [CoinbaseProvider]
