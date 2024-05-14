from allauth.socialaccount.providers.base import ProviderAccount
from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider
from allauth.socialaccount.providers.tiktok.scope import TikTokScope
from allauth.socialaccount.providers.tiktok.views import TikTokOAuth2Adapter


class TikTokAccount(ProviderAccount):
    def get_username(self):
        return self.account.extra_data.get("username")

    def get_display_name(self):
        return self.account.extra_data.get("display_name")

    def get_profile_url(self):
        return self.account.extra_data.get("profile_deep_link")

    def get_avatar_url(self):
        return self.account.extra_data.get("avatar_url")

    def to_str(self):
        username = self.get_username()
        return username or super().to_str()


class TikTokProvider(OAuth2Provider):
    id = "tiktok"
    name = "TikTok"
    account_class = TikTokAccount
    oauth2_adapter_class = TikTokOAuth2Adapter
    pkce_enabled_default = False

    def extract_uid(self, data):
        return str(data["open_id"])

    def extract_common_fields(self, data):
        # TikTok does not provide an email address
        return {
            "username": data.get("username") or data.get("display_name"),
            "name": data.get("display_name"),
        }

    def get_default_scope(self):
        # Requires LoginKit and Scopes with user.info.basic and user.info.profile enabled
        return [TikTokScope.user_info_basic.value, TikTokScope.user_info_profile.value]


provider_classes = [TikTokProvider]
