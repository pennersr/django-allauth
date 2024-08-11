from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.stocktwits.views import (
    StocktwitsOAuth2Adapter,
)


class StocktwitsAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("user", {}).get("avatar_url_ssl")

    def get_user_data(self):
        return self.account.extra_data.get("user", {})


class StocktwitsProvider(OAuth2Provider):
    id = "stocktwits"
    name = "Stocktwits"
    account_class = StocktwitsAccount
    oauth2_adapter_class = StocktwitsOAuth2Adapter

    def extract_uid(self, data):
        return str(data["user"]["id"])

    def extract_common_fields(self, data):
        return dict(
            full_name=data.get("user", {}).get("name"),
        )


provider_classes = [StocktwitsProvider]
