from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth.provider import OAuthProvider
from allauth.socialaccount.providers.xing.views import XingOAuthAdapter


class XingAccount(ProviderAccount):
    def get_profile_url(self):
        return self.account.extra_data.get("permalink")

    def get_avatar_url(self):
        return self.account.extra_data.get("photo_urls", {}).get("large")

    def to_str(self):
        dflt = super().to_str()
        return self.account.extra_data.get("active_email") or dflt


class XingProvider(OAuthProvider):
    id = "xing"
    name = "Xing"
    account_class = XingAccount
    oauth_adapter_class = XingOAuthAdapter

    def extract_uid(self, data):
        return data["id"]

    def extract_common_fields(self, data):
        return dict(
            email=data.get("active_email"),
            username=data.get("page_name"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )


provider_classes = [XingProvider]
