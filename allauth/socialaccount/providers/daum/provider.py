from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DaumAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("bigImagePath")

    def to_str(self):
        return self.account.extra_data.get("nickname", self.account.uid)


class DaumProvider(OAuth2Provider):
    id = "Daum"
    name = "Daum"
    account_class = DaumAccount

    def extract_uid(self, data):
        return str(data.get("id"))


provider_classes = [DaumProvider]
