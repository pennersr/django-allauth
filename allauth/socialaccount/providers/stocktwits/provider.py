from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class StocktwitsAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("user", {}).get("avatar_url_ssl")

    def to_str(self):
        dflt = super(StocktwitsAccount, self).to_str()
        return self.account.extra_data.get("user", {}).get("name", dflt)


class StocktwitsProvider(OAuth2Provider):
    id = "stocktwits"
    name = "Stocktwits"
    account_class = StocktwitsAccount

    def extract_uid(self, data):
        return data.get("user", {}).get("id")

    def extract_common_fields(self, data):
        return dict(
            full_name=data.get("user", {}).get("name"),
        )


provider_classes = [StocktwitsProvider]
