from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.dingtalk.views import (
    DingTalkOAuth2Adapter,
)
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider


class DingTalkAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("avatarUrl")

    def to_str(self):
        return self.account.extra_data.get(
            "nick", super(DingTalkAccount, self).to_str()
        )


class DingTalkProvider(OAuth2Provider):
    id = "dingtalk"
    name = "DingTalk"
    account_class = DingTalkAccount
    oauth2_adapter_class = DingTalkOAuth2Adapter

    def extract_uid(self, data):
        return data["openId"]

    def get_default_scope(self):
        return ["openid", "corpid"]

    def extract_common_fields(self, data):
        return dict(username=data.get("nick"), name=data.get("nick"))


provider_classes = [DingTalkProvider]
