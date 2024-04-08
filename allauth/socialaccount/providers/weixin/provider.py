from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.weixin.views import WeixinOAuth2Adapter


class WeixinAccount(ProviderAccount):
    def get_avatar_url(self):
        return self.account.extra_data.get("headimgurl")

    def to_str(self):
        return self.account.extra_data.get(
            "nickname", super(WeixinAccount, self).to_str()
        )


class WeixinProvider(OAuth2Provider):
    id = "weixin"
    name = "Weixin"
    account_class = WeixinAccount
    oauth2_adapter_class = WeixinOAuth2Adapter

    def extract_uid(self, data):
        return data["openid"]

    def get_default_scope(self):
        return ["snsapi_login"]

    def extract_common_fields(self, data):
        return dict(username=data.get("nickname"), name=data.get("nickname"))


provider_classes = [WeixinProvider]
