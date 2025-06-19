from allauth.socialaccount.providers.base import ProviderAccount, ProviderException
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.weibo.views import WeiboOAuth2Adapter


class WeiboAccount(ProviderAccount):
    def get_profile_url(self):
        # profile_url = "u/3195025850"
        return "http://www.weibo.com/" + self.account.extra_data.get("profile_url")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_large")


class WeiboProvider(OAuth2Provider):
    id = "weibo"
    name = "Weibo"
    account_class = WeiboAccount
    oauth2_adapter_class = WeiboOAuth2Adapter

    def extract_uid(self, data):
        ret = data.get("idstr")
        if not ret:
            raise ProviderException("Missing 'idstr'")
        return ret

    def extract_common_fields(self, data):
        return dict(username=data.get("screen_name"), name=data.get("name"))


provider_classes = [WeiboProvider]
