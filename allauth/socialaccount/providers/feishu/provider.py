from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.feishu.views import FeishuOAuth2Adapter
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class FeishuAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_big")


class FeishuProvider(OAuth2Provider):
    id = "feishu"
    name = "feishu"
    account_class = FeishuAccount
    oauth2_adapter_class = FeishuOAuth2Adapter

    def extract_uid(self, data):
        return data["open_id"]

    def extract_common_fields(self, data):
        return dict(username=data.get("name"), name=data.get("name"))


provider_classes = [FeishuProvider]
